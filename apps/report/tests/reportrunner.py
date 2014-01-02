import glob
import time
import os
import json
import logging

from django.test import TestCase, Client
from django.core import management
from django.utils.datastructures import SortedDict

from project import settings

from apps.datasource.models import Job
from apps.datasource.forms import TableFieldForm
from apps.report.models import Report, Section, Widget, WidgetJob

logger = logging.getLogger(__name__)

class ReportRunnerTestCase(TestCase):

    report = None
    
    @classmethod
    def setUpClass(cls):
        initial_data = glob.glob(os.path.join(settings.PROJECT_ROOT,
                                              'apps', 'report', 'tests',
                                              '*.json'))
        management.call_command('loaddata', *initial_data)

        path = 'apps.report.tests.reports.' + cls.report
        logger.info("Loading report: %s" % path)
        management.call_command('reload', report_name=path)

    def setUp(self):
        logger.info('Logging in as admin')
        logger.info('Report count: %d' % len(Report.objects.all()))
        self.client = Client()
        self.assertTrue(self.client.login(username='admin', password='admin'))
        
    def run_report(self, criteria, expect_fail=False):
        logger.info("Running report %s with criteria:\n%s" %
                    (self.report, criteria))

        response = self.client.post('/report/%s/' % self.report,
                                    data=criteria)

        sc = response.status_code
        if (sc >= 400 and sc < 500):
            logger.info("Report erroro response code %s\n%s" %
                        (sc, response.content))
            self.assertTrue(expect_fail)
            return

        self.assertEqual(response.status_code, 200)

        report_data = json.loads(response.content)
        widgets = {}
        for widget_data in report_data[1:]:
            wid = widget_data['widgetid']
            widget = Widget.objects.get(id=wid)
            logger.info('Processing widget %s' % widget)

            # POST to the widget url to create the WidgetJob instance
            widget_url = widget_data['posturl']
            widget_criteria = widget_data['criteria']
            postdata = {'criteria': json.dumps(widget_criteria)}
            response = self.client.post(widget_url, data=postdata)
            self.assertEqual(response.status_code, 200)
            
            widgetjob_data = json.loads(response.content)

            # Extract the job url and get the first response
            joburl = widgetjob_data['joburl']
            widgets[joburl] = None
            
        for joburl in widgets:
            while True:
                response = self.client.get(joburl)
                job_data = json.loads(response.content)
                widgets[joburl] = job_data
                if widgets[joburl]['status'] not in [Job.COMPLETE, Job.ERROR]:
                    time.sleep(0.1)
                else:
                    break

        return widgets

