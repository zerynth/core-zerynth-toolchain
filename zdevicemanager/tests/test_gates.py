import logging
import sys
import unittest

from click.testing import CliRunner

from .context import cli
from .utils import _result_to_json
from .utils import randomString

log = logging.getLogger("ZDM_cli_test")
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class GatesTestSuite(unittest.TestCase):
    """gates test cases."""

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()
        cls.runner.invoke(cli, ['login', "--user", "testzdm@zerynth.com", "--passwd", "Pippo123"])


    def test_webhook_start(self):
        name = "test" + randomString()
        url = "https://" + randomString() + ".com"
        period = 10

        result = self.runner.invoke(cli, ["-J", 'workspace', 'all'])
        self.assertEqual(result.exit_code, 0)
        rjson = _result_to_json(result)
        wks_id = rjson[0]['id']
        tag = "test"

        result = self.runner.invoke(cli, ["-J", 'webhook', 'start', name, url, str(period), wks_id, '--tag', tag, '--origin', 'events'])

        self.assertEqual(result.exit_code, 0)

    def test_webhook_all(self):
        result = self.runner.invoke(cli, ["-J", 'workspace', 'all'])
        self.assertEqual(result.exit_code, 0)
        rjson = _result_to_json(result)
        wks_id = rjson[0]['id']

        result = self.runner.invoke(cli, ['-J', 'webhook', 'all', wks_id])
        self.assertEqual(result.exit_code, 0)

    def test_webhook_delete(self):
        result = self.runner.invoke(cli, ['-J', 'workspace', 'all'])
        self.assertEqual(result.exit_code, 0)
        rjson = _result_to_json(result)
        wks_id = rjson[0]['id']

        name = "test" + randomString()
        url = "https://" + randomString() + ".com"
        period = 10
        tag = "test"

        result = self.runner.invoke(cli, ['-J', 'webhook', 'start', name, url, str(period), wks_id, '--tag', tag, '--origin', 'data'])
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(cli, ['-J', 'webhook', 'all', wks_id])
        self.assertEqual(result.exit_code, 0)

        rjson = _result_to_json(result)

        wbhk_id = rjson[0]['id']

        result = self.runner.invoke(cli, ['-J', 'webhook', 'delete', wbhk_id])
        self.assertEqual(result.exit_code, 0)

    def test_webhook_get(self):
        result = self.runner.invoke(cli, ['-J', 'workspace', 'all'])
        self.assertEqual(result.exit_code, 0)
        rjson = _result_to_json(result)
        wks_id = rjson[0]['id']

        name = "test" + randomString()
        url = "https://" + randomString() + ".com"
        period = 10
        tag = "test"

        result = self.runner.invoke(cli, ['-J', 'webhook', 'start', name, url, str(period), wks_id, '--tag', tag, '--origin', 'data'])
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(cli, ['-J', 'webhook', 'all', wks_id])
        self.assertEqual(result.exit_code, 0)

        rjson = _result_to_json(result)

        wbhk_id = rjson[0]['id']

        result = self.runner.invoke(cli, ['-J', 'webhook', 'get', wbhk_id])
        self.assertEqual(result.exit_code, 0)

    def test_webhook_enable(self):
        result = self.runner.invoke(cli, ['-J', 'workspace', 'all'])
        self.assertEqual(result.exit_code, 0)
        rjson = _result_to_json(result)
        wks_id = rjson[0]['id']

        name = "test" + randomString()
        url = "https://" + randomString() + ".com"
        period = 10
        tag = "test"

        result = self.runner.invoke(cli, ['-J', 'webhook', 'start', name, url, str(period), wks_id, '--tag', tag, '--origin', 'data'])
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(cli, ['-J', 'webhook', 'all', wks_id])
        self.assertEqual(result.exit_code, 0)

        rjson = _result_to_json(result)

        wbhk_id = rjson[0]['id']

        result = self.runner.invoke(cli, ['-J', 'webhook', 'enable', wbhk_id])
        self.assertEqual(result.exit_code, 0)

    def test_webhook_disable(self):
        result = self.runner.invoke(cli, ['-J', 'workspace', 'all'])
        self.assertEqual(result.exit_code, 0)
        rjson = _result_to_json(result)
        wks_id = rjson[0]['id']

        name = "test" + randomString()
        url = "https://" + randomString() + ".com"
        period = 10
        tag = "test"

        result = self.runner.invoke(cli, ['-J', 'webhook', 'start', name, url, str(period), wks_id, '--tag', tag, '--origin', 'data'])
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(cli, ['-J', 'webhook', 'all', wks_id])
        self.assertEqual(result.exit_code, 0)

        rjson = _result_to_json(result)

        wbhk_id = rjson[0]['id']

        result = self.runner.invoke(cli, ['-J', 'webhook', 'disable', wbhk_id])
        self.assertEqual(result.exit_code, 0)
