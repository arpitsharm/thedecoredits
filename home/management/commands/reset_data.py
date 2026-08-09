from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Product, ProductImage, Pricing, QuoteRequest, PhoneNumber, Review, Category


class Command(BaseCommand):
    help = 'Wipe all data and create fresh admin user'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Deleting all data...'))

        Review.objects.all().delete()
        self.stdout.write(f'  Reviews deleted')

        QuoteRequest.objects.all().delete()
        self.stdout.write(f'  Quote requests deleted')

        Pricing.objects.all().delete()
        self.stdout.write(f'  Pricings deleted')

        ProductImage.objects.all().delete()
        self.stdout.write(f'  Product images deleted')

        Product.objects.all().delete()
        self.stdout.write(f'  Products deleted')

        PhoneNumber.objects.all().delete()
        self.stdout.write(f'  Phone numbers deleted')

        Category.objects.all().delete()
        self.stdout.write(f'  Categories deleted')

        User.objects.filter(is_superuser=True).exclude(username='admin').delete()
        self.stdout.write(f'  Old superusers deleted')

        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            admin_user.set_password('rajiv@admin')
            admin_user.email = 'admin@thedecoredits.com'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user updated: admin / rajiv@admin'))
        else:
            User.objects.create_superuser(
                username='admin',
                email='admin@thedecoredits.com',
                password='rajiv@admin',
            )
            self.stdout.write(self.style.SUCCESS('Admin user created: admin / rajiv@admin'))

        self.stdout.write(self.style.SUCCESS('Done! Database wiped clean.'))
