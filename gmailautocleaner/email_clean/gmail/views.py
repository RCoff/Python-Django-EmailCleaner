from django.shortcuts import render, get_object_or_404, reverse, HttpResponseRedirect
from django.utils import timezone
from django.views import View
import pandas as pd

from email_clean.tasks import parse_gmail
from data.models import EmailStorage


# Create your views here.
class Display(View):
    template_name = 'emails.html'
    context = {'parsed_messages': pd.DataFrame(),
               'unsubscribable_emails': pd.DataFrame(),
               'critical_unread_messages': pd.DataFrame(),
               'total_messages': None,
               'unread_emails_count': None,
               'unread_emails_percent': None,
               'spam_emails_count': None,
               'trash_emails_count': None}

    def get(self, request, id):
        email_storage_obj = get_object_or_404(EmailStorage, id=id)
        if email_storage_obj.expiration:
            if email_storage_obj.expiration < timezone.now():
                email_storage_obj.clear()
                return HttpResponseRedirect(reverse('gmail-load'))

        parsed_messages = email_storage_obj.parsed_emails
        if not parsed_messages:
            self.context = {'loading': True,
                            'id': str(email_storage_obj.id),
                            'emails_count': len(email_storage_obj.raw_emails)}
            if email_storage_obj.parse_status == 'ns' or not email_storage_obj.task_id:
                task = parse_gmail.delay(request.session['credentials'], email_storage_obj.id)
                email_storage_obj.task_id = task.id
                email_storage_obj.save()

            return render(request, template_name=self.template_name, context=self.context)

        email_df = pd.DataFrame(parsed_messages)
        # group_count_df = df.groupby(by=['from-domain'])['id'].count()
        unsubscribable_emails = email_df[email_df['unsubscribe'] != ""].drop_duplicates(
            subset=['unsubscribe']).sort_values(
            by='domain')
        unread_percent_df = pd.pivot_table(email_df[['domain', 'status']], index='domain', columns='status',
                                           aggfunc=len,
                                           fill_value=0)
        unread_percent_df['Unread_%'] = 1 - (
                unread_percent_df['read'] / (unread_percent_df['unread'] + unread_percent_df['read']))
        unread_percent_df = unread_percent_df.sort_values(by=['unread', 'Unread_%'], ascending=False)
        unread_percent_df = unread_percent_df[
            (unread_percent_df['unread'] >= 10) & (unread_percent_df['Unread_%'] >= 0.75)]

        self.context.update({'parsed_messages': email_df,
                             'unsubscribable_emails': unsubscribable_emails,
                             'critical_unread_messages': unread_percent_df,
                             'total_messages': len(email_df.index),
                             'unread_emails_count': len(email_df[email_df['status'] == 'unread'].index),
                             'unread_emails_percent': round(
                                 (len(email_df[email_df['status'] == 'unread'].index) / len(email_df.index)) * 100, 1),
                             'spam_emails_count': len(email_df[email_df['is_spam'] == True].index),
                             'trash_emails_count': ''})

        return render(request, template_name=self.template_name, context={'loaded_emails': self.context,
                                                                          'retrieved_time': email_storage_obj.raw_emails_retrieval_time,})
