from django.core.management.base import BaseCommand
from datetime import datetime
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from update_manager import DjangoUpdateManager

class Command(BaseCommand):
    help = 'Update Django modules with progress tracking every 15 minutes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            type=int,
            default=20,
            help='Total duration in minutes (default: 20)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=15,
            help='Progress update interval in minutes (default: 15)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting Django modules update process...")
        self.stdout.write("=" * 60)
        
        updater = DjangoUpdateManager()
        updater.duration_minutes = options['duration']
        updater.update_interval = options['interval']
        
        try:
            updater.start_updates()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n⚠️  Update process interrupted by user"))
            updater.is_running = False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Unexpected error: {str(e)}"))
            updater.is_running = False
