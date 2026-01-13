"""
Task Executor - handles execution of Geant4 simulations and analysis
"""

import subprocess
import threading
import queue
from pathlib import Path
from typing import Callable, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes tasks with real-time output streaming"""
    
    def __init__(self):
        self.current_process: Optional[subprocess.Popen] = None
        self.output_queue: queue.Queue = queue.Queue()
        self.is_running = False
    
    def execute_command(
        self,
        command: str,
        cwd: Optional[Path] = None,
        env_vars: Optional[Dict[str, str]] = None,
        on_output: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[int], None]] = None,
    ) -> threading.Thread:
        """
        Execute command asynchronously with output streaming
        
        Returns thread object (not started)
        """
        
        def run():
            try:
                self.is_running = True
                logger.info(f"Starting task: {command}")
                
                self.current_process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=env_vars,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True,
                )
                
                # Stream stdout
                if self.current_process.stdout:
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line:
                            if on_output:
                                on_output(line.rstrip('\n'))
                            self.output_queue.put(('output', line))
                
                # Get return code
                returncode = self.current_process.wait()
                self.is_running = False
                
                logger.info(f"Task completed with code: {returncode}")
                
                if on_complete:
                    on_complete(returncode)
                
                self.output_queue.put(('complete', returncode))
                
            except Exception as e:
                logger.error(f"Task error: {e}")
                if on_error:
                    on_error(str(e))
                self.is_running = False
                self.output_queue.put(('error', str(e)))
        
        thread = threading.Thread(target=run, daemon=True)
        return thread
    
    def stop(self):
        """Stop current process"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
            logger.info("Task terminated")
    
    def get_output(self) -> Optional[tuple]:
        """Get next output from queue"""
        try:
            return self.output_queue.get_nowait()
        except queue.Empty:
            return None
    
    def clear_queue(self):
        """Clear output queue"""
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break
