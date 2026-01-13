"""
Integrated Analysis Module - для роботи з NCC-02 даними
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SpectraAnalyzer:
    """Analyze gamma-ray spectra from Geant4 simulations"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.spectra_data = {}
        self.reactions_data = {}
    
    def discover_energy_directories(self) -> List[Tuple[str, Path]]:
        """Discover all energy subdirectories"""
        energies = []
        
        for item in self.data_dir.iterdir():
            if item.is_dir() and item.name.startswith("results"):
                energies.append((item.name.replace("results ", "").strip(), item))
        
        return sorted(energies, key=lambda x: self._energy_value(x[0]))
    
    @staticmethod
    def _energy_value(energy_str: str) -> float:
        """Parse energy string to float for sorting"""
        if energy_str == "":
            return -1
        
        parts = energy_str.split()
        if len(parts) >= 2:
            value = float(parts[0])
            return value
        return 0
    
    def load_spectra(self, csv_file: Path) -> Dict:
        """Load spectrum data from CSV file"""
        try:
            with open(csv_file, 'r') as f:
                content = f.read()
            
            # Parse sections
            spectrum_section = self._extract_section(content, "[SPECTRUM]")
            reactions_section = self._extract_section(content, "[REACTIONS]")
            summary_section = self._extract_section(content, "[SUMMARY]")
            
            return {
                'spectrum': self._parse_csv_section(spectrum_section),
                'reactions': self._parse_csv_section(reactions_section),
                'summary': summary_section,
            }
        except Exception as e:
            logger.error(f"Error loading {csv_file}: {e}")
            return {}
    
    @staticmethod
    def _extract_section(content: str, section_name: str) -> str:
        """Extract section from CSV content"""
        try:
            start = content.index(f"{section_name}\n")
            start = content.index("\n", start) + 1
            
            end = content.find("[", start + 1)
            if end == -1:
                end = len(content)
            
            return content[start:end]
        except ValueError:
            return ""
    
    @staticmethod
    def _parse_csv_section(section: str) -> pd.DataFrame:
        """Parse CSV section into DataFrame"""
        if not section.strip():
            return pd.DataFrame()
        
        try:
            from io import StringIO
            return pd.read_csv(StringIO(section))
        except:
            return pd.DataFrame()
    
    def plot_spectra_comparison(
        self,
        output_file: Path,
        material: str = "pure_sample"
    ):
        """Plot spectrum comparison across energies"""
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        for energy, energy_dir in self.discover_energy_directories():
            csv_file = energy_dir / f"data_{material}.csv"
            
            if csv_file.exists():
                data = self.load_spectra(csv_file)
                
                if 'spectrum' in data and not data['spectrum'].empty:
                    spectrum_df = data['spectrum']
                    
                    if 'Energy' in spectrum_df.columns and 'Count' in spectrum_df.columns:
                        ax.loglog(
                            spectrum_df['Energy'],
                            spectrum_df['Count'],
                            marker='o',
                            label=energy if energy else "Default",
                            markersize=3,
                        )
        
        ax.set_xlabel("Energy (keV)", fontsize=12)
        ax.set_ylabel("Counts", fontsize=12)
        ax.set_title(f"Gamma-ray Spectra Comparison - {material}", fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        logger.info(f"Saved spectra plot to {output_file}")
        plt.close()
    
    def plot_reactions_comparison(
        self,
        output_file: Path,
        material: str = "pure_sample"
    ):
        """Plot reactions composition per energy"""
        
        fig, axes = plt.subplots(
            1, len(self.discover_energy_directories()),
            figsize=(16, 4),
            sharey=True
        )
        
        for idx, (energy, energy_dir) in enumerate(self.discover_energy_directories()):
            csv_file = energy_dir / f"data_{material}.csv"
            
            if csv_file.exists():
                data = self.load_spectra(csv_file)
                
                if 'reactions' in data and not data['reactions'].empty:
                    reactions_df = data['reactions']
                    
                    if len(reactions_df) > 0:
                        ax = axes[idx] if len(axes.shape) > 0 else axes
                        
                        reactions_df.plot(
                            x='Particle' if 'Particle' in reactions_df.columns else 0,
                            y='Count' if 'Count' in reactions_df.columns else 1,
                            kind='bar',
                            ax=ax,
                            legend=False,
                        )
                        
                        ax.set_title(energy if energy else "Default", fontsize=10)
                        ax.set_xlabel("")
                        ax.tick_params(axis='x', rotation=45)
        
        fig.suptitle(f"Reactions Composition - {material}", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        logger.info(f"Saved reactions plot to {output_file}")
        plt.close()
    
    def generate_summary_report(self, output_file: Optional[Path] = None):
        """Generate summary report of all data"""
        
        report_lines = [
            "═" * 80,
            "GAMMA-RAY SPECTRA ANALYSIS REPORT",
            "═" * 80,
            "",
        ]
        
        for energy, energy_dir in self.discover_energy_directories():
            report_lines.append(f"Energy: {energy if energy else 'Default'}")
            report_lines.append("─" * 80)
            
            for material in ["pure_sample", "reactant_sample"]:
                csv_file = energy_dir / f"data_{material}.csv"
                
                if csv_file.exists():
                    data = self.load_spectra(csv_file)
                    
                    if 'spectrum' in data and not data['spectrum'].empty:
                        spectrum_df = data['spectrum']
                        
                        # Top peaks
                        if 'Count' in spectrum_df.columns:
                            top_peaks = spectrum_df.nlargest(5, 'Count')
                            
                            report_lines.append(f"\n  Material: {material.upper()}")
                            report_lines.append(f"  Top 5 Peaks:")
                            
                            for _, peak in top_peaks.iterrows():
                                energy_kev = peak.get('Energy', 'N/A')
                                count = peak.get('Count', 'N/A')
                                report_lines.append(f"    - {energy_kev} keV: {count} counts")
            
            report_lines.append("")
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Saved report to {output_file}")
        
        return report_text


def run_analysis(data_dir: Path, output_dir: Optional[Path] = None):
    """Run complete analysis"""
    
    if output_dir is None:
        output_dir = data_dir
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    analyzer = SpectraAnalyzer(data_dir)
    
    # Generate plots
    analyzer.plot_spectra_comparison(
        output_dir / "spectra_pure_sample.png",
        "pure_sample"
    )
    analyzer.plot_spectra_comparison(
        output_dir / "spectra_reactant_sample.png",
        "reactant_sample"
    )
    analyzer.plot_reactions_comparison(
        output_dir / "reactions_pure_sample.png",
        "pure_sample"
    )
    analyzer.plot_reactions_comparison(
        output_dir / "reactions_reactant_sample.png",
        "reactant_sample"
    )
    
    # Generate report
    report = analyzer.generate_summary_report(
        output_dir / "analysis_report.txt"
    )
    
    print(report)


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    data_dir = Path("Release")
    
    if data_dir.exists():
        run_analysis(data_dir)
    else:
        print(f"Data directory not found: {data_dir}")
