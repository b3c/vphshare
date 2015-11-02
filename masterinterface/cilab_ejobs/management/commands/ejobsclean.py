from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError
from cilab_ejobs.models import EJob
from datetime import date, timedelta

class Command(BaseCommand):
    args = '<past_days past_days ...>'
    help = 'Clean all finished ejobs with past_days old'

    def handle(self, *args, **options):
        for pass_days in args:
            try:
                days = int(pass_days)
                date_start = date(2015,1,1)
                date_end = date.today() - timedelta(days=days)
                ejobs = EJob.objects.filter(
                        Q(state__gt=1),
                        Q(modification_timestamp__range=(date_start,date_end)) )
                for ejob in ejobs:
                    self.stdout.write('ob: %s' % str(ejob))
                    ejob.delete()

            except Exception, e:
                raise CommandError('Something was wrong with %s ex: %s' % (pass_days,str(e)))

            self.stdout.write('Successfully cleaned finished ejobs with %s' % pass_days)
