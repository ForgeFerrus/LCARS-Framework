# ◤ TITANIUM JOURNAL AI ANALYZER
# LCARS Framework :: AI_ANALYSIS // GEMMA_INTEGRATION // CHANGE_INSIGHTS
# ОПИС: AI аналіз змін коду для бортового журналу.
# СТАНДАРТ: Titanium CamelCase, Zero-Except.

from __future__ import annotations
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import re
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import List, Dict, Optional
# Titanium Bridge Migration: from dataclasses import dataclass

from lcars.base.info import getVersion

__version__ = getVersion()


@dataclass
class AnalysisResult:
    # Результат AI аналізу
    Summary: str
    Impact: str  # LOW, MEDIUM, HIGH, CRITICAL
    Components: List[str]
    Recommendations: List[str]


class JournalAIAnalyzer:
    # AI аналізатор змін для журналу

    def __init__(self, RootPath: Path = None):
        self.RootPath = RootPath or Path(".")
        self.HasGemma = self.CheckGemma()

    def CheckGemma(self) -> bool:
        # Перевірка наявності Gemma/Ollama
        Result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        return "gemma" in Result.stdout.lower() if Result.returncode == 0 else False

    def GetDiffContent(self, MaxLines: int = 100) -> str:
        # Отримання тексту змін
        Result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            cwd=self.RootPath
        )

        if Result.returncode != 0:
            return ""

        Lines = Result.stdout.split("\n")[:MaxLines]
        return "\n".join(Lines)

    def AnalyzeWithGemma(self, DiffContent: str) -> AnalysisResult:
        # Аналіз через Gemma
        if not self.HasGemma:
            return self.FallbackAnalysis(DiffContent)

        Prompt = self.BuildPrompt(DiffContent)

        Result = subprocess.run(
            ["ollama", "run", "gemma:2b"],
            input=Prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if Result.returncode != 0:
            return self.FallbackAnalysis(DiffContent)

        return self.ParseGemmaOutput(Result.stdout)

    def BuildPrompt(self, DiffContent: str) -> str:
        # Побудова промпта для Gemma
        return f"""Analyze these code changes for LCARS Framework:

{DiffContent[:2000]}

Provide brief analysis in this format:
SUMMARY: One sentence describing the changes
IMPACT: LOW/MEDIUM/HIGH/CRITICAL
COMPONENTS: Comma-separated list of affected components
RECOMMENDATIONS: One recommendation per line

Keep response under 300 characters."""

    def ParseGemmaOutput(self, Output: str) -> AnalysisResult:
        # Парсинг відповіді Gemma
        Summary = "AI analysis unavailable"
        Impact = "UNKNOWN"
        Components = []
        Recommendations = []

        for Line in Output.split("\n"):
            Line = Line.strip()
            if Line.startswith("SUMMARY:"):
                Summary = Line.replace("SUMMARY:", "").strip()
            elif Line.startswith("IMPACT:"):
                Impact = Line.replace("IMPACT:", "").strip().upper()
            elif Line.startswith("COMPONENTS:"):
                CompStr = Line.replace("COMPONENTS:", "").strip()
                Components = [C.strip() for C in CompStr.split(",") if C.strip()]
            elif Line.startswith("RECOMMENDATIONS:"):
                continue
            elif Line and not Line.startswith(("SUMMARY", "IMPACT", "COMPONENTS")):
                if len(Line) > 10:
                    Recommendations.append(Line)

        return AnalysisResult(
            Summary=Summary[:200],
            Impact=Impact if Impact in ["LOW", "MEDIUM", "HIGH", "CRITICAL"] else "UNKNOWN",
            Components=Components[:5],
            Recommendations=Recommendations[:3]
        )

    def FallbackAnalysis(self, DiffContent: str) -> AnalysisResult:
        # Резервний аналіз без AI
        Lines = DiffContent.split("\n")

        # Підрахунок змін за типами файлів
        PyChanges = len([L for L in Lines if L.endswith(".py")])
        MdChanges = len([L for L in Lines if L.endswith(".md")])
        TestChanges = len([L for L in Lines if "test" in L.lower()])

        Components = []
        if PyChanges > 0:
            Components.append("Python modules")
        if MdChanges > 0:
            Components.append("Documentation")
        if TestChanges > 0:
            Components.append("Tests")

        # Визначення impact
        TotalLines = len(Lines)
        if TotalLines > 500:
            Impact = "HIGH"
        elif TotalLines > 100:
            Impact = "MEDIUM"
        else:
            Impact = "LOW"

        return AnalysisResult(
            Summary=f"Code changes detected: {PyChanges} Python files, {MdChanges} docs",
            Impact=Impact,
            Components=Components if Components else ["Unknown"],
            Recommendations=["Review changes manually"]
        )

    def AnalyzeChanges(self) -> AnalysisResult:
        # Головний метод аналізу
        Diff = self.GetDiffContent()
        if not Diff:
            return AnalysisResult(
                Summary="No changes detected",
                Impact="NONE",
                Components=[],
                Recommendations=["No action required"]
            )

        return self.AnalyzeWithGemma(Diff)


# API функції
def AnalyzeWithAI() -> AnalysisResult:
    # Швидкий аналіз через AI
    Analyzer = JournalAIAnalyzer()
    return Analyzer.AnalyzeChanges()


def GetImpactBadge(Impact: str) -> str:
    # Отримання бейджа для impact
    Badges = {
        "CRITICAL": "🔴 CRITICAL",
        "HIGH": "🟠 HIGH",
        "MEDIUM": "🟡 MEDIUM",
        "LOW": "🟢 LOW",
        "NONE": "⚪ NONE",
        "UNKNOWN": "⚫ UNKNOWN"
    }
    return Badges.get(Impact, "⚫ UNKNOWN")


__all__ = ["JournalAIAnalyzer", "AnalyzeWithAI", "AnalysisResult", "GetImpactBadge"]
