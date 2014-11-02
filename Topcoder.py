import sublime, sublime_plugin, sys, os, copy

class TopcoderCommand(sublime_plugin.TextCommand): 
  def find_line_offset(self, content, target, row_offset):
    # returns the text found, the beginning of found, end of found, and target_region which is found + offset line
    begin = content.find(target)
    if begin == -1:
        return ("", -1, -1, None)
    end = begin + len(target)
    target_region = sublime.Region(begin, end)
    row, _ = self.view.rowcol(target_region.a)
    next_row_starting = self.view.text_point(row + row_offset, 0)
    target_region = self.view.full_line(next_row_starting)
    n = self.view.substr(target_region)
    return (n, begin, end, target_region)

  def generate_test_cases(self, example_strs, signature, className):
    # returns a list of dicts, each with testCase str (singline for now), and expectation string
    result = []
    # use state machine
    LEFT = 0
    INSIDE = 1
    RESULT = 2
    COMMENT = 3
    mode = LEFT
    current_example = ""
    current_comment = ""
    r = None
    for line in example_strs.split("\n"):
      if (line == ""):
        continue
      if (mode == LEFT):
        if "{" in line:
          current_example = current_example + line.replace("{","(").replace("}",")")
          mode = INSIDE
        if "}" in line:
          mode = RESULT
      elif (mode == INSIDE):
        current_example = current_example + ":" + line.replace("{","(").replace("}",")")
        if "}" in line:
          mode = RESULT
      elif (mode == RESULT):
        if "Returns" in line:
          return_value = line.split(":")[1]
          r = dict()
          r["example_str"] = current_example
          r["return_value"] = return_value
          mode = COMMENT
      elif (mode == COMMENT):
        if "{" in line or "}" in line:
          # wrap up
          r["comment"] = current_comment[:-1]
          result.append(r)
          current_example = ""
          current_comment = ""

          # comment is over
          if "{" in line:
            current_example = current_example + line.replace("{","(").replace("}",")")
            mode = INSIDE
          if "}" in line:
            mode = RESULT
        elif any(c.isalpha() for c in line.strip()):
          # keep mode as comment
          current_comment = current_comment + line + ":"

    # might end up waiting for a {} to add to array, catch last case
    if (mode == COMMENT):
      r["comment"] = current_comment[:-1]
      result.append(r)
      current_example = ""
      current_comment = ""

    return result

  def write_line(self, new_file, edit, point, s):
    insert_len = new_file.insert(edit, point, s + "\n")
    point = point + insert_len
    return point

  def run(self, edit):
    # parse active view for content
    # find class name
    content = self.view.substr(sublime.Region(0, self.view.size()))
    class_name_result = self.find_line_offset(content, "Class",1)
    class_name = class_name_result[0].replace("\n","")
    if (class_name == ""):
      print "no class name found, not in topcoder format, done"
      return

    # find signature
    signature_result = self.find_line_offset(content, "Method signature",1)
    signature = signature_result[0].replace("\n","")
    if ("def" not in signature):
      print "topcoder format maybe, but no python signature found, done"
      return

    # find number of parameters
    parameter_result = self.find_line_offset(content, "Parameters",1)
    parameters = parameter_result[0].replace("\n","")
    numParameters = len(parameters.split(","))
    print numParameters

    # find examples and do parsing
    examples_start_result = self.find_line_offset(content, "Examples",0)
    examples_end_result = self.find_line_offset(content, "This problem statement",-1)
    examples_region = sublime.Region(examples_start_result[1], examples_end_result[1])
    example_str = self.view.substr(examples_region).encode(sys.getfilesystemencoding())
    example_str = os.linesep.join([s for s in example_str.splitlines() if s]) # reduces number of newlines that ar blank

    # parse examples and generate tests using class name and signature
    test_cases = self.generate_test_cases(example_str, signature, class_name)

    # now we open a new window and dump everything into it
    new_file = sublime.active_window().new_file()
    point = 0
    # insert class name
    class_str = "class " + class_name + ":\n"
    point = self.write_line(new_file, edit, point, class_str)

    # insert signature
    sig_str = "\t" + signature + "\n"
    point = self.write_line(new_file, edit, point, sig_str)

    # insert some spaces
    fill_str =  "\n\n# Test cases\n"
    point = self.write_line(new_file, edit, point, fill_str)

    # instantiate object
    inst_str = "inst = " + class_name + "()\n"
    point = self.write_line(new_file, edit, point, inst_str)

    # insert test cases
    for i in range(len(test_cases)):
      d = test_cases[i]

      e_str = "example" + str(i) + " = " + d["example_str"].replace(":","")
      point = self.write_line(new_file, edit, point, e_str)

      run_str = "result = inst(example" + str(i) + ")"
      point = self.write_line(new_file, edit, point, run_str)

      comment_str = "#" + d["comment"].replace(":", "\n# ")
      point = self.write_line(new_file, edit, point, comment_str)

      assert_str = "assert( result == " + d["return_value"] + ")"
      point = self.write_line(new_file, edit, point, assert_str)

      # insert some spaces
      point = self.write_line(new_file, edit, point, "")

    #finally, save as file using class name
    file_name = class_name + ".py"
    self.view.file_name = file_name
    new_file.run_command("save")

# Todos:
# 1. handle multiple argument signatures
# 2. handle other topcoder languages
# 3. refactor code for handling test cases