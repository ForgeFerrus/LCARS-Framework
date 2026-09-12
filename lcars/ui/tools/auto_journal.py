# ◤ TITANIUM AUTO-JOURNAL
# LCARS Framework :: BORTOVYI_ZHURNAL // CHANGE_TRACKING // AI_ANALYSIS
# ОПИС: Автоматичне ведення бортового журналу на основі git змін.
# СТАНДАРТ: Titanium CamelCase, Zero-Except.

from __future__ import annotations
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import re
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from typing import List, Dict, Optional
# Titanium Bridge Migration: from dataclasses import dataclass

from lcars.base.info import getVersion
from tools.journal_ai import JournalAIAnalyzer, AnalysisResult

__version__ = getVersion()


@dataclass
class ChangeEntry:
    # Запис про зміну
    FilePath: str
    ChangeType: str  # A-dded, M-odified, D-eleted, R-enamed
    LinesAdded: int = 0
    LinesRemoved: int = 0
    Description: str = ""


class AutoJournal:
    # Автоматичний журнал змін

    def __init__(self, RootPath: Path = None):
        self.RootPath = RootPath or Path(".")
        self.JournalDir = self.RootPath / "lcars" / "journal"
        self.JournalDir.mkdir(parents=True, exist_ok=True)

    def GetGitDiff(self) -> str:
        # Отримання змін з git
        Result = subprocess.run(
            ["git", "diff", "--stat", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            cwd=self.RootPath
        )
        return Result.stdout if Result.returncode == 0 else ""

    def GetGitLog(self, Count: int = 10) -> List[Dict]:
        # Отримання останніх комітів
        Result = subprocess.run(
            ["git", "log", f"-{Count}", "--pretty=format:%H|%s|%ad|%an", "--date=short"],
            capture_output=True,
            text=True,
            cwd=self.RootPath
        )

        Commits = []
        if Result.returncode == 0:
            for Line in Result.stdout.strip().split("\n"):
                Parts = Line.split("|")
                if len(Parts) >= 4:
                    Commits.append({
                        "hash": Parts[0][:8],
                        "message": Parts[1],
                        "date": Parts[2],
                        "author": Parts[3]
                    })
        return Commits

    def GetChangedFiles(self) -> List[ChangeEntry]:
        # Аналіз змінених файлів
        Result = subprocess.run(
            ["git", "diff", "--numstat", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            cwd=self.RootPath
        )

        Changes = []
        if Result.returncode == 0:
            for Line in Result.stdout.strip().split("\n"):
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

                    Changes.append(ChangeEntry(
                        FilePath=FilePath,
                        ChangeType=ChangeType,
                        LinesAdded=Added,
                        LinesRemoved=Removed
                    ))

        return Changes

    def CategorizeChanges(self, Changes: List[ChangeEntry]) -> Dict[str, List[ChangeEntry]]:
        # Категоризація змін
        Categories = {
            "CORE": [],
            "MODULES": [],
            "SERVICES": [],
            "UI": [],
            "TESTS": [],
            "DOCS": [],
            "OTHER": []
        }

        for Change in Changes:
            Path = Change.FilePath.lower()
            if "core/" in Path or "base/" in Path:
                Categories["CORE"].append(Change)
            elif "modules/" in Path:
                Categories["MODULES"].append(Change)
            elif "service/" in Path or "services/" in Path:
                Categories["SERVICES"].append(Change)
            elif "ui/" in Path:
                Categories["UI"].append(Change)
            elif "test" in Path:
                Categories["TESTS"].append(Change)
            elif Path.endswith(".md") or "docs/" in Path:
                Categories["DOCS"].append(Change)
            else:
                Categories["OTHER"].append(Change)

        return Categories

    def GenerateEntry(self, Commits: List[Dict], Changes: List[ChangeEntry], AIAnalysis: AnalysisResult = None) -> str:
        # Генерація запису журналу
        Now = datetime.now()
        DateStr = Now.strftime("%Y-%m-%d")
        TimeStr = Now.strftime("%H:%M:%S")

        Lines = [
            f"# ◤ БОРТОВИЙ ЖУРНАЛ: {DateStr}",
            f"# ЧАС: {TimeStr}",
            f"# ВЕРСІЯ: {__version__}",
            "",
            "## AI АНАЛІЗ ЗМІН",
            ""
        ]

        # AI аналіз
        if AIAnalysis:
            Lines.extend([
                f"**Рівень впливу:** {AIAnalysis.Impact}",
                f"",
                f"**Короткий опис:** {AIAnalysis.Summary}",
                f"",
                f"**Компоненти:** {', '.join(AIAnalysis.Components) if AIAnalysis.Components else 'N/A'}",
                f"",
            ])
            if AIAnalysis.Recommendations:
                Lines.append("**Рекомендації:**")
                for Rec in AIAnalysis.Recommendations:
                    Lines.append(f"- {Rec}")
                Lines.append("")

        Lines.extend([
            "## СТАТИСТИКА ЗМІН",
            ""
        ])

        # Статистика
        TotalFiles = len(Changes)
        TotalAdded = sum(C.LinesAdded for C in Changes)
        TotalRemoved = sum(C.LinesRemoved for C in Changes)

        Lines.extend([
            f"- Файлів змінено: {TotalFiles}",
            f"- Рядків додано: +{TotalAdded}",
            f"- Рядків видалено: -{TotalRemoved}",
            ""
        ])

        # Категоризація
        Categories = self.CategorizeChanges(Changes)
        Lines.append("## КАТЕГОРІЇ ЗМІН")
        Lines.append("")

        for CatName, CatChanges in Categories.items():
            if CatChanges:
                Lines.append(f"### {CatName}: {len(CatChanges)} файлів")
                for Change in CatChanges:
                    Symbol = {"A": "+", "M": "~", "D": "-"}.get(Change.ChangeType, "?")
                    Lines.append(f"  {Symbol} {Change.FilePath} (+{Change.LinesAdded}/-{Change.LinesRemoved})")
                Lines.append("")

        # Останні коміти
        Lines.extend([
            "## КОМІТИ",
            ""
        ])

        for Commit in Commits[:5]:
            Lines.append(f"- `{Commit['hash']}` {Commit['message']} ({Commit['author']})")

        Lines.extend([
            "",
            "---",
            f"*Запис згенеровано автоматично AutoJournal v{__version__}*"
        ])

        return "\n".join(Lines)

    def WriteJournal(self):
        # Запис журналу
        Commits = self.GetGitLog(5)
        Changes = self.GetChangedFiles()

        if not Changes and not Commits:
            print("◤ AUTO_JOURNAL :: NO_CHANGES_DETECTED")
            return

        # AI аналіз змін
        print("◤ AUTO_JOURNAL :: AI_ANALYZING...")
        Analyzer = JournalAIAnalyzer(self.RootPath)
        AIAnalysis = Analyzer.AnalyzeChanges()

        Content = self.GenerateEntry(Commits, Changes, AIAnalysis)
        DateStr = datetime.now().strftime("%Y-%m-%d")
        FilePath = self.JournalDir / f"auto_{DateStr}.md"

        with open(FilePath, "w", encoding="utf-8") as F:
            F.write(Content)

        print(f"◤ AUTO_JOURNAL :: WRITTEN: {FilePath}")
        print(f"◤ AUTO_JOURNAL :: FILES: {len(Changes)}, COMMITS: {len(Commits)}")
        print(f"◤ AUTO_JOURNAL :: IMPACT: {AIAnalysis.Impact}")


# Функції API
def UpdateJournal():
    # Оновити журнал
    Journal = AutoJournal()
    Journal.WriteJournal()


def GetTodayChanges() -> List[ChangeEntry]:
    # Отримати сьогоднішні зміни
    Journal = AutoJournal()
    return Journal.GetChangedFiles()


__all__ = ["AutoJournal", "UpdateJournal", "GetTodayChanges", "ChangeEntry"]


if __name__ == "__main__":
    print("◤ AUTO_JOURNAL :: STARTING")
    UpdateJournal()
    print("◤ AUTO_JOURNAL :: COMPLETE")
