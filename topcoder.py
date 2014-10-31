import sublime, sublime_plugin, sys, os

class TopcoderCommand(sublime_plugin.TextCommand): 
  def find_line_offset(self, content, target, row_offset):
    # returns the text found, the beginning of found, end of found, and target_region which is found + offset line
    begin = content.find(target)
    if begin == -1:
        return
    end = begin + len(target)
    print begin
    target_region = sublime.Region(begin, end)
    row, _ = self.view.rowcol(target_region.a)
    next_row_starting = self.view.text_point(row + row_offset, 0)
    target_region = self.view.full_line(next_row_starting)
    n = self.view.substr(target_region)
    return (n, begin, end, target_region)

  def run(self, edit):
    # parse active view for content
    # find class name
    content = self.view.substr(sublime.Region(0, self.view.size()))
    class_name_result = self.find_line_offset(content, "Class",1)
    print class_name_result[0]

    # find signature
    signature_result = self.find_line_offset(content, "Method signature",1)
    print signature_result[0]

    # find examples and do parsing
    examples_start_result = self.find_line_offset(content, "Examples",0)
    examples_end_result = self.find_line_offset(content, "This problem statement",-1)
    examples_region = sublime.Region(examples_start_result[1], examples_end_result[1])
    example_str = self.view.substr(examples_region).encode(sys.getfilesystemencoding())
    example_str = os.linesep.join([s for s in example_str.splitlines() if s])
    print example_str