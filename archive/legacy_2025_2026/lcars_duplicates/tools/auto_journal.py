from __future__ import annotations
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from lcars.base.version import getVersion
from tools.journal import AnalysisResult, JournalAIAnalyzer

@dataclass
class ChangeEntry:
    FilePath: str
    ChangeType: str
    LinesAdded: int = 0
    LinesRemoved: int = 0
    Description: str = ""
    __version__ = getVersion()

class AutoJournal:
    def __init__(self, RootPath: Path | None = None):
        self.RootPath = RootPath or Path(".")
        self.JournalDir = self.RootPath / "lcars" / "journal"
        self.JournalDir.mkdir(parents=True, exist_ok=True)

    def GetGitDiff(self) -> str:
        Result = subprocess.run(
            ["git", "diff", "--stat", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            cwd=self.RootPath,
        )
        return Result.stdout if Result.returncode == 0 else ""

    def GetGitLog(self, Count: int = 10) -> List[Dict[str, str]]:
        Result = subprocess.run(
            ["git", "log", f"-{Count}", "--pretty=format:%H|%s|%ad|%an", "--date=short"],
            capture_output=True,
            text=True,
            cwd=self.RootPath,
        )

        Commits: List[Dict[str, str]] = []
        if Result.returncode == 0:
            for Line in Result.stdout.strip().splitlines():
                Parts = Line.split("|")
                if len(Parts) >= 4:
                    Commits.append(
                        {
                            "hash": Parts[0][:8],
                            "message": Parts[1],
                            "date": Parts[2],
                            "author": Parts[3],
                        }
                    )
        return Commits

    def GetChangedFiles(self) -> List[ChangeEntry]:
        Result = subprocess.run(
            ["git", "diff", "--numstat", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            cwd=self.RootPath,
        )

        Changes: List[ChangeEntry] = []
        if Result.returncode == 0:
            for Line in Result.stdout.strip().splitlines():
                Match = re.match(r"(\d+)\s+(\d+)\s+(.+)", Line)
                if Match:
                    Added = int(Match.group(1))
                    Removed = int(Match.group(2))
                    FilePath = Match.group(3)

                    ChangeType = "M"
                    if Added > 0 and Removed == 0:
                        ChangeType = "A"
                    elif Added == 0 and Removed > 0:
                        ChangeType = "D"

                    Changes.append(
                        ChangeEntry(
                            FilePath=FilePath,
                            ChangeType=ChangeType,
                            LinesAdded=Added,
                            LinesRemoved=Removed,
                        )
                    )

        return Changes

    def CategorizeChanges(self, Changes: List[ChangeEntry]) -> Dict[str, List[ChangeEntry]]:
        Categories: Dict[str, List[ChangeEntry]] = {
            "CORE": [],
            "MODULES": [],
            "SERVICES": [],
            "UI": [],
            "TESTS": [],
            "DOCS": [],
            "OTHER": [],
        }

        for Change in Changes:
            FilePath = Change.FilePath.lower()
            if "core/" in FilePath or "base/" in FilePath:
                Categories["CORE"].append(Change)
            elif "modules/" in FilePath:
                Categories["MODULES"].append(Change)
            elif "service/" in FilePath or "services/" in FilePath:
                Categories["SERVICES"].append(Change)
            elif "ui/" in FilePath:
                Categories["UI"].append(Change)
            elif "test" in FilePath:
                Categories["TESTS"].append(Change)
            elif FilePath.endswith(".md") or "docs/" in FilePath:
                Categories["DOCS"].append(Change)
            else:
                Categories["OTHER"].append(Change)

        return Categories

    def GenerateEntry(
        self,
        Commits: List[Dict[str, str]],
        Changes: List[ChangeEntry],
        AIAnalysis: AnalysisResult | None = None,
    ) -> str:
        Now = datetime.now()
        DateStr = Now.strftime("%Y-%m-%d")
        TimeStr = Now.strftime("%H:%M:%S")

        Lines = [
            f"# WORKSPACE : {DateStr}",
            f"# TIME: {TimeStr}",
            f"# VERSION: {__version__}",
            "",
            "## AI ANALYSIS",
            "",
        ]

        if AIAnalysis:
            Lines.extend(
                [
                    f"**Impact:** {AIAnalysis.Impact}",
                    "",
                    f"**Summary:** {AIAnalysis.Summary}",
                    "",
                    f"**Components:** {', '.join(AIAnalysis.Components) if AIAnalysis.Components else 'N/A'}",
                    "",
                ]
            )
            if AIAnalysis.Recommendations:
                Lines.append("**Recommendations:**")
                for Rec in AIAnalysis.Recommendations:
                    Lines.append(f"- {Rec}")
                Lines.append("")

        Lines.extend(
            [
                "## CHANGE STATISTICS",
                "",
            ]
        )

        TotalFiles = len(Changes)
        TotalAdded = sum(Item.LinesAdded for Item in Changes)
        TotalRemoved = sum(Item.LinesRemoved for Item in Changes)

        Lines.extend(
            [
                f"- Files changed: {TotalFiles}",
                f"- Lines added: +{TotalAdded}",
                f"- Lines removed: -{TotalRemoved}",
                "",
            ]
        )

        Categories = self.CategorizeChanges(Changes)
        Lines.append("## CATEGORIZED CHANGES")
        Lines.append("")

        for CatName, CatChanges in Categories.items():
            if CatChanges:
                Lines.append(f"### {CatName}: {len(CatChanges)} files")
                for Change in CatChanges:
                    Symbol = {"A": "+", "M": "~", "D": "-"}.get(Change.ChangeType, "?")
                    Lines.append(f"  {Symbol} {Change.FilePath} (+{Change.LinesAdded}/-{Change.LinesRemoved})")
                Lines.append("")

        Lines.extend(
            [
                "## COMMITS",
                "",
            ]
        )

        for Commit in Commits[:5]:
            Lines.append(f"- `{Commit['hash']}` {Commit['message']} ({Commit['author']})")

        Lines.extend(
            [
                "",
                "---",
                f"*Generated automatically by AutoJournal v{__version__}*",
            ]
        )

        return "\n".join(Lines)

    def WriteJournal(self) -> Path | None:
        Commits = self.GetGitLog(5)
        Changes = self.GetChangedFiles()

        if not Changes and not Commits:
            print("AUTO_JOURNAL :: NO_CHANGES_DETECTED")
            return None

        print("AUTO_JOURNAL :: AI_ANALYZING...")
        Analyzer = JournalAIAnalyzer(self.RootPath)
        AIAnalysis = Analyzer.AnalyzeChanges()

        Content = self.GenerateEntry(Commits, Changes, AIAnalysis)
        DateStr = datetime.now().strftime("%Y-%m-%d")
        FilePath = self.JournalDir / f"auto_{DateStr}.md"

        with open(FilePath, "w", encoding="utf-8") as FileHandle:
            FileHandle.write(Content)

        print(f"AUTO_JOURNAL :: WRITTEN: {FilePath}")
        print(f"AUTO_JOURNAL :: FILES: {len(Changes)}, COMMITS: {len(Commits)}")
        print(f"AUTO_JOURNAL :: IMPACT: {AIAnalysis.Impact}")
        return FilePath


def UpdateJournal() -> None:
    Journal = AutoJournal()
    Journal.WriteJournal()


def GetTodayChanges() -> List[ChangeEntry]:
    Journal = AutoJournal()
    return Journal.GetChangedFiles()


def main() -> int:
    print("AUTO_JOURNAL :: STARTING")
    UpdateJournal()
    print("AUTO_JOURNAL :: COMPLETE")
    return 0


__all__ = ["AutoJournal", "UpdateJournal", "GetTodayChanges", "ChangeEntry", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
