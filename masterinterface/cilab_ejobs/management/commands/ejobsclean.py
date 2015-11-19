from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cilab_ejobs.models import EJob
from datetime import timedelta

class Command(BaseCommand):
    args = '<past_days past_days ...>'
    help = 'Clean all finished ejobs with past_days old'

    def handle(self, *args, **options):
        for pass_days in args:
            try:
                days = int(pass_days)
                date_end = timezone.now() - timedelta(days=days)
                ejobs = EJob.objects.filter(
                    Q(state__gt=1),
                    ~Q(state=3),
                    Q(modification_timestamp__lte=date_end) )
                for ejob in ejobs:
                    self.stdout.write('ob: %s\n' % str(ejob.id))
                    ejob.delete()

            except Exception, e:
                raise CommandError('Something was wrong with %s ex: %s' % (pass_days,str(e)))

            self.stdout.write('Successfully cleaned finished ejobs with %s\n' % pass_days)
