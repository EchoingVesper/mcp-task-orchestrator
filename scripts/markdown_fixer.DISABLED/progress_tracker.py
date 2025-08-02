"""
Progress Tracker for monitoring markdown fixing progress.

Provides real-time progress updates and ETA estimation.
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FileResult:
    """Result of processing a single file."""
    file_path: Path
    success: bool
    errors_before: int
    errors_after: int
    processing_time: float
    error_message: Optional[str] = None
    backup_created: bool = False


@dataclass
class ProgressStats:
    """Statistics for progress tracking."""
    total_files: int
    processed_files: int = 0
    successful_fixes: int = 0
    failed_fixes: int = 0
    total_errors_fixed: int = 0
    start_time: float = field(default_factory=time.time)
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0
    processing_rate: float = 0.0


class ProgressTracker:
    """Tracks progress of markdown fixing operations."""
    
    def __init__(self, total_files: int, verbose: bool = True):
        """
        Initialize progress tracker.
        
        Args:
            total_files: Total number of files to process
            verbose: Whether to print detailed progress
        """
        self.stats = ProgressStats(total_files=total_files)
        self.verbose = verbose
        self.results: List[FileResult] = []
        self.failed_files: List[Path] = []
        
    def start(self) -> None:
        """Start progress tracking."""
        self.stats.start_time = time.time()
        if self.verbose:
            print(f"🚀 Starting markdown fixing for {self.stats.total_files} files...")
            print("=" * 60)
    
    def update(self, result: FileResult) -> None:
        """
        Update progress with a file result.
        
        Args:
            result: Result of processing a file
        """
        self.results.append(result)
        self.stats.processed_files += 1
        
        if result.success:
            self.stats.successful_fixes += 1
            self.stats.total_errors_fixed += (result.errors_before - result.errors_after)
        else:
            self.stats.failed_fixes += 1
            self.failed_files.append(result.file_path)
        
        # Update timing statistics
        self.stats.elapsed_time = time.time() - self.stats.start_time
        if self.stats.processed_files > 0:
            self.stats.processing_rate = self.stats.processed_files / self.stats.elapsed_time
            remaining_files = self.stats.total_files - self.stats.processed_files
            if self.stats.processing_rate > 0:
                self.stats.estimated_remaining = remaining_files / self.stats.processing_rate
        
        if self.verbose:
            self._print_progress(result)
    
    def _print_progress(self, result: FileResult) -> None:
        """Print progress update for a single file."""
        status = "✅" if result.success else "❌"
        percentage = (self.stats.processed_files / self.stats.total_files) * 100
        
        # Format file path for display
        file_display = str(result.file_path)
        if len(file_display) > 50:
            file_display = "..." + file_display[-47:]
        
        # Format timing info
        eta_str = self._format_time(self.stats.estimated_remaining)
        rate_str = f"{self.stats.processing_rate:.1f} files/s"
        
        if result.success:
            errors_fixed = result.errors_before - result.errors_after
            print(f"{status} [{self.stats.processed_files:3d}/{self.stats.total_files}] "
                  f"({percentage:5.1f}%) {file_display:<50} | "
                  f"Fixed: {errors_fixed:2d} errors | "
                  f"Time: {result.processing_time:.2f}s | "
                  f"ETA: {eta_str} | Rate: {rate_str}")
        else:
            print(f"{status} [{self.stats.processed_files:3d}/{self.stats.total_files}] "
                  f"({percentage:5.1f}%) {file_display:<50} | "
                  f"FAILED: {result.error_message or 'Unknown error'}")
    
    def finish(self) -> None:
        """Finish progress tracking and print summary."""
        self.stats.elapsed_time = time.time() - self.stats.start_time
        
        if self.verbose:
            print("=" * 60)
            print("✨ Markdown fixing completed!")
            print()
            self._print_summary()
    
    def _print_summary(self) -> None:
        """Print detailed summary of results."""
        print(f"📊 Summary:")
        print(f"   Total files:     {self.stats.total_files}")
        print(f"   Processed:       {self.stats.processed_files}")
        print(f"   Successful:      {self.stats.successful_fixes}")
        print(f"   Failed:          {self.stats.failed_fixes}")
        print(f"   Errors fixed:    {self.stats.total_errors_fixed}")
        print()
        
        print(f"⏱️  Timing:")
        print(f"   Total time:      {self._format_time(self.stats.elapsed_time)}")
        print(f"   Average rate:    {self.stats.processing_rate:.2f} files/s")
        
        if self.stats.successful_fixes > 0:
            avg_time = self.stats.elapsed_time / self.stats.successful_fixes
            print(f"   Avg per file:    {avg_time:.2f}s")
        print()
        
        # Success rate
        success_rate = (self.stats.successful_fixes / self.stats.total_files) * 100
        if success_rate == 100:
            print("🎉 All files processed successfully!")
        else:
            print(f"📈 Success rate: {success_rate:.1f}%")
        
        # Show failed files if any
        if self.failed_files:
            print()
            print("❌ Failed files:")
            for file_path in self.failed_files:
                print(f"   - {file_path}")
        
        # Show top error types fixed
        error_types = self._get_error_type_summary()
        if error_types:
            print()
            print("🔧 Top fixes applied:")
            for rule, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {rule}: {count} fixes")
    
    def _get_error_type_summary(self) -> Dict[str, int]:
        """Get summary of error types that were fixed."""
        # This would need to be populated by the fixer based on which rules were applied
        # For now, return empty dict
        return {}
    
    def _format_time(self, seconds: float) -> str:
        """Format time duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.0f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def get_stats(self) -> ProgressStats:
        """Get current progress statistics."""
        return self.stats
    
    def get_results(self) -> List[FileResult]:
        """Get all file processing results."""
        return self.results
    
    def get_failed_files(self) -> List[Path]:
        """Get list of files that failed processing."""
        return self.failed_files
    
    def export_results(self, output_path: Path) -> None:
        """
        Export detailed results to JSON file.
        
        Args:
            output_path: Path to output file
        """
        import json
        
        export_data = {
            "summary": {
                "total_files": self.stats.total_files,
                "processed_files": self.stats.processed_files,
                "successful_fixes": self.stats.successful_fixes,
                "failed_fixes": self.stats.failed_fixes,
                "total_errors_fixed": self.stats.total_errors_fixed,
                "elapsed_time": self.stats.elapsed_time,
                "processing_rate": self.stats.processing_rate
            },
            "results": [
                {
                    "file_path": str(result.file_path),
                    "success": result.success,
                    "errors_before": result.errors_before,
                    "errors_after": result.errors_after,
                    "processing_time": result.processing_time,
                    "error_message": result.error_message,
                    "backup_created": result.backup_created
                }
                for result in self.results
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)