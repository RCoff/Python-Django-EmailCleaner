import datetime

from django.shortcuts import render, get_object_or_404, reverse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views import View
import pandas as pd

from email_clean.utils import parse_retrieved_time
from email_clean.tasks import parse_gmail
from data.models import EmailStorage


# Create your views here.
class Display(LoginRequiredMixin, View):
    login_url = '/auth/gmail/sign-in'
    template_name = 'emails.html'
    context = {'parsed_messages': None,
               'unsubscribable_emails': None,
               'critical_unread_messages': None,
               'total_messages': None,
               'unread_emails_count': None,
               'unread_emails_percent': None,
               'spam_emails_count': None,
               'trash_emails_count': None}

    def get(self, request, id):
        email_storage_obj = get_object_or_404(EmailStorage, id=id)
        if not email_storage_obj.expiration and email_storage_obj.raw_emails_retrieval_time:
            email_storage_obj.expiration = email_storage_obj.raw_emails_retrieval_time + datetime.timedelta(hours=24)
            email_storage_obj.save()
        if email_storage_obj.expiration:
            if email_storage_obj.expiration < timezone.now():
                email_storage_obj.clear()
                return HttpResponseRedirect(reverse('gmail-load'))

        parsed_messages = email_storage_obj.parsed_emails
        if not parsed_messages:
            self.context = {'loading': True,
                            'id': str(email_storage_obj.task.task_id),
                            'emails_count': len(email_storage_obj.raw_emails)}

            return render(request, template_name=self.template_name, context=self.context)

        # TODO: Statistics by sender
        # TODO: Over time?

        email_df = pd.DataFrame(parsed_messages)
        email_df['date-received'] = pd.to_datetime(email_df['date-received'], errors='coerce')
        # group_count_df = df.groupby(by=['from-domain'])['id'].count()
        # unsubscribable_emails_json = EmailStorage.objects.filter(id=id, parsed_emails__unsubscribe__isnull=False)

        # Get emails received in the last 90 days that are unsubscribable
        unsubscribable_emails = email_df[~email_df['unsubscribe'].isnull()] \
            .sort_values(by='date-received', ascending=True) \
            .drop_duplicates(subset=['domain'], keep='last')
        unsubscribable_emails = unsubscribable_emails[
            unsubscribable_emails['date-received'] >= (timezone.now() - datetime.timedelta(days=90))]

        # Get emails that are the most unread by sender
        unread_percent_df = pd.pivot_table(email_df[['sender', 'status']], index='sender', columns='status',
                                           aggfunc=len,
                                           fill_value=0)
        unread_percent_df = unread_percent_df.merge(
            email_df[['sender', 'date-received']].groupby(by=['sender'], as_index=True, sort=False).max(),
            left_index=True, right_index=True, how='left').rename(columns={'date-received': 'date_received'})
        unread_percent_df['Unread_pct'] = round((1 - (
                unread_percent_df['read'] / (unread_percent_df['unread'] + unread_percent_df['read']))) * 100, 0)
        unread_percent_df = unread_percent_df.sort_values(by=['unread', 'Unread_pct'], ascending=False)
        unread_percent_df = unread_percent_df[
            (unread_percent_df['unread'] >= 10) & (unread_percent_df['Unread_pct'] >= 0.75)]

        self.context.update({'unsubscribable_emails': unsubscribable_emails,
                             'critical_unread_messages': unread_percent_df,
                             'total_messages': len(email_df.index),
                             'unread_emails_count': len(email_df[email_df['status'] == 'unread'].index),
                             'unread_emails_percent': round(
                                 (len(email_df[email_df['status'] == 'unread'].index) / len(email_df.index)) * 100, 1),
                             'spam_emails_count': len(email_df[email_df['is_spam'] == True].index),
                             'trash_emails_count': ''})
        retrieved_time = parse_retrieved_time(email_storage_obj.raw_emails_retrieval_time)

        return render(request, template_name=self.template_name, context={'loaded_emails': self.context,
                                                                          'retrieved_time': retrieved_time})
