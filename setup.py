from setuptools import setup, find_packages

setup(
    name="lcars-framework",
    version="0.1.0-alpha",
    description="LCARS Framework - Star Trek inspired UI framework",
    author="LCARS Development Team",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        # GUI Framework
        "PyQt6>=6.0.0",
        "PyQt6-Qt6>=6.0.0",
        "PyQt6-sip>=13.0.0",
        
        # Data Processing
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        
        # System utilities
        "psutil>=5.8.0",
        
        # Logging and utilities
        "python-dotenv>=0.19.0",
        "PyYAML>=6.0.0",
        
        # Optional but recommended
        "scipy>=1.7.0",  # For advanced data analysis
        
        # 3D Visualization
        "vispy>=0.14.0",  # GPU-accelerated 3D graphics
        "PyOpenGL>=3.1.5",  # OpenGL bindings
        
        # AI Models
        "transformers>=4.40.0",
        "torch>=2.0.0",
        "kagglehub>=0.3.0",
        "accelerate>=0.30.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Multimedia :: Graphics",
    ],
    entry_points={
        "console_scripts": [
            "lcars-desktop=lcars.base.desktop:Run",
        ],
    },
)
