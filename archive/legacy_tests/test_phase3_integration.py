"""
Unit tests for Phase 3 Integration
Тестування нових функцій: volume calculation, JSON loading, GDML/C++ export, 3D viz
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.core.geant4_wrapper import (
    Simulation, Detector, DetectorComponent, DetectorShape, 
    Vector3D, Material, MaterialType, Particle, ParticleType, PhysicsList
)
from lcars.core.blender_connector import DetectorBuilder, MaterialEnum, GeometryType
from lcars.core.visualizer_3d import Particle3DTrajectory, Vispy3DCanvas
import numpy as np


class TestVolumeCalculation(unittest.TestCase):
    """Test DetectorComponent volume calculations"""
    
    def test_box_volume(self):
        """Test BOX volume calculation"""
        component = DetectorComponent(
            name="test_box",
            shape=DetectorShape.BOX,
            dimensions=Vector3D(x=4.0, y=3.0, z=2.0)
        )
        
        detector = Detector(name="test")
        detector.add_component(component)
        volume = detector.calculate_volume()
        
        expected = 4.0 * 3.0 * 2.0  # 24.0
        self.assertAlmostEqual(volume, expected, places=2)
    
    def test_cylinder_volume(self):
        """Test CYLINDER volume calculation"""
        component = DetectorComponent(
            name="test_cylinder",
            shape=DetectorShape.CYLINDER,
            dimensions=Vector3D(x=2.0, y=2.0, z=5.0)  # radius=1.0, height=5.0
        )
        
        detector = Detector(name="test")
        detector.add_component(component)
        volume = detector.calculate_volume()
        
        import math
        expected = math.pi * 1.0**2 * 5.0  # π * r² * h
        self.assertAlmostEqual(volume, expected, places=1)
    
    def test_multiple_components(self):
        """Test volume with multiple components"""
        detector = Detector(name="test")
        
        box = DetectorComponent(
            name="box",
            shape=DetectorShape.BOX,
            dimensions=Vector3D(x=2.0, y=2.0, z=2.0)
        )
        
        cylinder = DetectorComponent(
            name="cylinder",
            shape=DetectorShape.CYLINDER,
            dimensions=Vector3D(x=1.0, y=1.0, z=2.0)
        )
        
        detector.add_component(box)
        detector.add_component(cylinder)
        volume = detector.calculate_volume()
        
        # 8 + π*0.5²*2 = 8 + π = ~11.14
        self.assertGreater(volume, 8.0)
        self.assertLess(volume, 12.0)


class TestJSONLoading(unittest.TestCase):
    """Test JSON configuration saving and loading"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_save_and_load_simple(self):
        """Test save and load cycle"""
        # Create and configure simulation
        sim1 = Simulation("test_sim", self.temp_path)
        sim1.configure_from_ncc02(sample_type="pure", energy_mev=0.0253)
        sim1.num_events = 5000
        
        # Save to JSON
        config_file = self.temp_path / "test_config.json"
        sim1.save_config(config_file)
        self.assertTrue(config_file.exists())
        
        # Load from JSON
        sim2 = Simulation("loaded_sim", self.temp_path)
        sim2.load_config(config_file)
        
        # Verify loaded data
        self.assertEqual(sim2.name, "loaded_sim")  # Name comes from constructor
        self.assertEqual(sim2.num_events, 5000)
        self.assertIsNotNone(sim2.detector)
        self.assertIsNotNone(sim2.primary_particle)
        self.assertIsNotNone(sim2.physics_list)
        self.assertEqual(sim2.status, "loaded")
    
    def test_json_structure(self):
        """Test JSON structure is valid"""
        sim = Simulation("test", self.temp_path)
        sim.configure_from_ncc02()
        
        config_file = self.temp_path / "structure_test.json"
        sim.save_config(config_file)
        
        # Read and validate JSON
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('name', data)
        self.assertIn('detector', data)
        self.assertIn('primary_particle', data)
        self.assertIn('physics_list', data)
        self.assertIn('num_events', data)


class TestGDMLExport(unittest.TestCase):
    """Test GDML export functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_gdml_export_creates_file(self):
        """Test GDML export creates valid XML file"""
        builder = DetectorBuilder()
        builder.build_ncc02()
        
        gdml_file = self.temp_path / "detector.gdml"
        result = builder.export_to_gdml(gdml_file)
        
        self.assertTrue(result)
        self.assertTrue(gdml_file.exists())
        
        # Verify it's valid XML
        with open(gdml_file, 'r') as f:
            content = f.read()
        
        self.assertIn('<?xml', content)
        self.assertIn('<gdml', content)
        self.assertIn('</gdml>', content)
        self.assertIn('<materials>', content)
        self.assertIn('<solids>', content)
    
    def test_gdml_contains_elements(self):
        """Test GDML contains expected elements"""
        builder = DetectorBuilder()
        builder.add_crystal("Crystal", MaterialEnum.COBALT_59)
        builder.add_shield("Shield", MaterialEnum.LEAD)
        
        gdml_file = self.temp_path / "elements_test.gdml"
        builder.export_to_gdml(gdml_file)
        
        with open(gdml_file, 'r') as f:
            content = f.read()
        
        # Check for components
        self.assertIn('Cobalt59', content)
        self.assertIn('Lead', content)


class TestCppExport(unittest.TestCase):
    """Test C++ export functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_cpp_export_creates_files(self):
        """Test C++ export creates .hh and .cc files"""
        builder = DetectorBuilder()
        builder.build_ncc02()
        
        cpp_file = self.temp_path / "DetectorConstruction"
        result = builder.export_to_cpp(cpp_file)
        
        self.assertTrue(result)
        
        # Check both files created
        h_file = self.temp_path / "DetectorConstruction.hh"
        cc_file = self.temp_path / "DetectorConstruction.cc"
        
        self.assertTrue(h_file.exists())
        self.assertTrue(cc_file.exists())
    
    def test_cpp_contains_geant4_code(self):
        """Test C++ export contains Geant4 API calls"""
        builder = DetectorBuilder()
        builder.build_ncc02()
        
        cpp_file = self.temp_path / "TestClass"
        builder.export_to_cpp(cpp_file, class_name="TestClass")
        
        cc_file = self.temp_path / "TestClass.cc"
        with open(cc_file, 'r') as f:
            content = f.read()
        
        # Check for Geant4 includes and classes
        self.assertIn('G4VUserDetectorConstruction', content)
        self.assertIn('G4NistManager', content)
        self.assertIn('G4Material', content)
        self.assertIn('G4LogicalVolume', content)


class TestVisualization(unittest.TestCase):
    """Test 3D visualization enhancements"""
    
    def test_trajectory_creation(self):
        """Test Particle3DTrajectory creation and properties"""
        positions = np.array([
            [0, 0, 0],
            [1, 1, 1],
            [2, 2, 2]
        ])
        
        trajectory = Particle3DTrajectory(
            particle_id=1,
            particle_type='electron',
            positions=positions,
            energy_keV=100.0
        )
        
        self.assertEqual(trajectory.particle_id, 1)
        self.assertEqual(trajectory.particle_type, 'electron')
        self.assertGreater(trajectory.length, 0)
        self.assertEqual(trajectory.energy_keV, 100.0)
        
        # Check color assignment
        self.assertEqual(trajectory.color_rgb, (1.0, 0.5, 0.0))  # Orange for electron
    
    def test_particle_color_assignment(self):
        """Test automatic color assignment by particle type"""
        particles = [
            ('gamma', (0.0, 1.0, 1.0)),
            ('neutron', (0.5, 1.0, 0.5)),
            ('proton', (1.0, 0.0, 0.0)),
        ]
        
        positions = np.array([[0, 0, 0], [1, 1, 1]])
        
        for ptype, expected_color in particles:
            traj = Particle3DTrajectory(1, ptype, positions, 10.0)
            self.assertEqual(traj.color_rgb, expected_color,
                           f"Wrong color for {ptype}")
    
    def test_trajectory_path_length(self):
        """Test path length calculation"""
        # Create trajectory along diagonal
        positions = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [1, 1, 1]
        ])
        
        trajectory = Particle3DTrajectory(1, 'electron', positions, 10.0)
        
        # Expected: 1 + 1 + sqrt(2) ≈ 3.414
        self.assertAlmostEqual(trajectory.length, 3.414, places=2)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_full_workflow_geant4(self):
        """Test complete workflow: configure -> save -> load -> export"""
        # Create simulation
        sim = Simulation("NCC-02-Full-Test", self.temp_path)
        sim.configure_from_ncc02(sample_type="pure", energy_mev=0.5)
        
        # Save configuration
        config_file = self.temp_path / "ncc02_config.json"
        sim.save_config(config_file)
        
        # Load configuration
        sim_loaded = Simulation("loaded", self.temp_path)
        sim_loaded.load_config(config_file)
        
        # Export to GDML
        builder = DetectorBuilder()
        builder.build_ncc02()
        gdml_file = self.temp_path / "ncc02.gdml"
        gdml_result = builder.export_to_gdml(gdml_file)
        
        # Export to C++
        cpp_file = self.temp_path / "NCC02Detector"
        cpp_result = builder.export_to_cpp(cpp_file)
        
        # Verify all steps succeeded
        self.assertTrue(config_file.exists())
        self.assertEqual(sim_loaded.status, "loaded")
        self.assertTrue(gdml_result)
        self.assertTrue(cpp_result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
