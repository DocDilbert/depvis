import os


def traverse_all_files_in_dir(path):
    files = (
        os.path.join(path, i)
        for i in os.listdir(path)
        if os.path.isfile(os.path.join(path, i))
    )
    for i in files:
        yield i


def traverse_all_source_files_in_dir(path):
    for i in traverse_all_files_in_dir(path):
        if ".cpp" in i or ".h" in i or ".c" in i:
            yield i


def traverse_all_source_file_content_in_dir(path):
    for i in traverse_all_source_files_in_dir(path):
        with open(i, "r") as file:
            data = file.read()
            yield i, data


class PerfRegExMatches:
    """This class, when called, traverses through all source files in the given directory path, reads
    them to memory and counts the number of matches of regex.
    """

    def __init__(self, regex):
        self.regex_ = regex

    def __call__(self, node_id, node):
        path = node['path']
        cnt = 0
        occurences = []
        for filename_with_path, content in traverse_all_source_file_content_in_dir(path):
            occ = len(self.regex_.findall(content))
            _, filename = os.path.split(filename_with_path)
            if occ > 0:
                occurences.append("%s [%i]" % (filename, occ))

            cnt += occ

        return {"occurences": cnt, "files": occurences}
