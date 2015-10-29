import unittest
import json
import re

def render(data, template):
  def get_key(obj, key):
    return None if obj is None else obj.get(key)

  def replace(match):
    return reduce(get_key, match.group(1).split('.'), data)

  return re.sub(r'{([^}]+)}', replace, template)

# tests

fixture = json.loads("""{"name":"project","url":"job/project/","build":{"full_url":"http://jenkins/project/15/","number":15,"phase":"FINALIZED","status":"SUCCESS","url":"job/sap-migrator/15/","scm":{"url":"git","branch":"origin/master","commit":"abc"},"log":"[...truncated 206 lines...]\\nFinished Calculation of disk usage of workspace in 0 seconds\\nFinished: SUCCESS\\n","artifacts":{"project.jar":{"archive":"http://jenkins/project"}}}}""")

class TestStringMethods(unittest.TestCase):

  def test_template(self):
    self.assertEqual(render(fixture, """{name}: {build.phase} - {build.status} {build.full_url}
{build.log}"""), """project: FINALIZED - SUCCESS http://jenkins/project/15/
[...truncated 206 lines...]
Finished Calculation of disk usage of workspace in 0 seconds
Finished: SUCCESS
""")

  def test_no_key(self):
    self.assertEqual(render(fixture, "a{does.not.exist}b"), "ab")
