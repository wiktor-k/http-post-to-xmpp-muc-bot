import unittest
import json
import re
import sys

value_replace = re.compile('{([^/][^ }]+)}', re.MULTILINE | re.DOTALL)
map_replace = re.compile('{map ([^ /}]+)}(.*?){/map}', re.MULTILINE | re.DOTALL)

def render(data, template):
  def get_key(obj, key):
    return None if obj is None else obj.get(key)

  def replaceMap(match):
    container = get_key(data, match.group(1))
    subtemplate = match.group(2)
    def in_scope(obj):
      if not isinstance(obj, dict):
        return render(obj, subtemplate)
      obj[''] = data.get('')
      data[''] = obj
      text = render(data, subtemplate)
      data[''] = obj['']
      return text
    return ''.join(map(in_scope, container))

  # replace maps
  text = re.sub(map_replace, replaceMap, template)
  
  # replace access to properties
  def replace(match):
    return reduce(get_key, match.group(1).split('.'), data)

  text = re.sub(value_replace, replace, text)
  
  # replace objects themselves
  text = text.replace('{}', str(data))
  
  return text

# tests

fixture = json.loads("""{"name":"project","url":"job/project/","build":{"full_url":"http://jenkins/project/15/","number":15,"phase":"FINALIZED","status":"SUCCESS","url":"job/project/15/","scm":{"url":"git","branch":"origin/master","commit":"abc"},"log":"[...truncated 206 lines...]\\nFinished Calculation of disk usage of workspace in 0 seconds\\nFinished: SUCCESS\\n","artifacts":{"project.jar":{"archive":"http://jenkins/project"}}},"commits":[{"name":"one"},{"name":"two"},{"name":"three"}],"strings":["a","b","c"]}""")

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

  def test_map(self):
    self.assertEqual(render(fixture, "a-{map commits}{.name}-{/map}"), "a-one-two-three-")
    self.assertEqual(render(fixture, "a-{map commits}{.name}-{/map}{name}"), "a-one-two-three-project")
    self.assertEqual(render(fixture, "a-{map strings}{}-{/map}{name}"), "a-a-b-c-project")
    
  def test_multiline_map(self):
    self.assertEqual(render(fixture, "a-\n{map commits}\n{.name}-\n{/map}"), "a-\n\none-\n\ntwo-\n\nthree-\n")

if __name__ == "__main__":
  print render(json.loads('\n'.join(sys.stdin.readlines())), sys.argv[1])