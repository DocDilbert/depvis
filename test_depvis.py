from unittest.mock import MagicMock, call, ANY
from unittest import mock
from depvis import GraphFromDirectory, traverse_dirgraph_dfs


def create_GraphFromDirectory(generate_root=True):
    graph_from_dir = GraphFromDirectory(generate_root=generate_root)

    return graph_from_dir


def create_StubDirWalker_2DirsSimple(main_dir="test"):
    stub_dir_walker = MagicMock()
    stub_dir_walker.walk.return_value = [
        ["a\\b\\%s" % (main_dir), ["dir1"], ["file1"]],
        ["a\\b\\%s\\dir1" % (main_dir), [], ["file2"]],
    ]
    return stub_dir_walker


def create_StubDirWalker_3DirsSimple(main_dir="test"):
    stub_dir_walker = MagicMock()
    stub_dir_walker.walk.return_value = [
        ["a\\b\\%s" % (main_dir), ["dir1", "dir2"], []],
        ["a\\b\\%s\\dir1" % (main_dir), [], []],
        ["a\\b\\%s\\dir2" % (main_dir), [], []],
    ]
    return stub_dir_walker


def create_StubDirWalker_3DirsHierachy(main_dir="test"):
    stub_dir_walker = MagicMock()
    stub_dir_walker.walk.return_value = [
        ["a\\b\\%s" % (main_dir), ["dir1"], ["file1"]],
        ["a\\b\\%s\\dir1" % (main_dir), ["dir2"], ["file2"]],
        ["a\\b\\%s\\dir1\\dir2" % (main_dir), [], []],
    ]
    return stub_dir_walker


def test_add_dir_1Dir2FilesWalk_StateChange2EdgesGraph():

    # Arrange
    graph_from_dir = create_GraphFromDirectory()

    stub_dir_walker = create_StubDirWalker_2DirsSimple()
    graph_from_dir.set_dir_walker(stub_dir_walker)

    # Act
    graph_from_dir.add_dir("a\\b\\test", [])

    # Assert
    edges, nodes = graph_from_dir.get_graph()
    assert nodes["root"]["name"] == "root"
    assert edges == {"node_0": {"node_1"}, "root": {"node_0"}}
    assert nodes == {
        "node_0": {"name": "test", "path": "a\\b\\test", "rank": 1},
        "node_1": {"name": "dir1", "path": "a\\b\\test\\dir1", "rank": 2},
        "root": {"name": "root", "path": ".\\", "rank": 0},
    }


def test_add_dir_1Dir2FilesWalkWithoutRoot_StateChange2EdgesGraph():

    # Arrange
    graph_from_dir = create_GraphFromDirectory(generate_root=False)

    stub_dir_walker = create_StubDirWalker_2DirsSimple()
    graph_from_dir.set_dir_walker(stub_dir_walker)

    # Act
    graph_from_dir.add_dir("a\\b\\test", [])

    # Assert
    edges, nodes = graph_from_dir.get_graph()
    assert "root" not in nodes
    assert edges == {"node_0": {"node_1"}}
    assert nodes == {
        "node_0": {"name": "test", "path": "a\\b\\test", "rank": 1},
        "node_1": {"name": "dir1", "path": "a\\b\\test\\dir1", "rank": 2},
    }


def test_add_dir_2DirsInOneDirectoryWalk_StateChange2EdgesGraph():

    # Arrange
    graph_from_dir = create_GraphFromDirectory()

    stub_dir_walker = create_StubDirWalker_3DirsSimple()
    graph_from_dir.set_dir_walker(stub_dir_walker)

    # Act
    graph_from_dir.add_dir("a\\b\\test", [])

    # Assert
    edges, nodes = graph_from_dir.get_graph()
    assert nodes["root"]["name"] == "root"
    assert edges == {"node_0": {"node_1", "node_2"}, "root": {"node_0"}}
    assert nodes == {
        "node_0": {"name": "test", "path": "a\\b\\test", "rank": 1},
        "node_1": {"name": "dir1", "path": "a\\b\\test\\dir1", "rank": 2},
        "node_2": {"name": "dir2", "path": "a\\b\\test\\dir2", "rank": 2},
        "root": {"name": "root", "path": ".\\", "rank": 0},
    }


def test_add_dir_2Dirs2FilesWalk_StateChange3EdgesGraph():

    # Arrange
    graph_from_dir = create_GraphFromDirectory()
    stub_dir_walker = create_StubDirWalker_3DirsHierachy()
    graph_from_dir.set_dir_walker(stub_dir_walker)

    # Act
    graph_from_dir.add_dir("a\\b\\test", [])

    # Assert
    edges, nodes = graph_from_dir.get_graph()

    assert nodes["root"]["name"] == "root"
    assert edges == {"node_0": {"node_1"}, "node_1": {"node_2"}, "root": {"node_0"}}
    assert nodes == {
        "node_0": {"name": "test", "path": "a\\b\\test", "rank": 1},
        "node_1": {"name": "dir1", "path": "a\\b\\test\\dir1", "rank": 2},
        "node_2": {"name": "dir2", "path": "a\\b\\test\\dir1\\dir2", "rank": 3},
        "root": {"name": "root", "path": ".\\", "rank": 0},
    }


def test_add_dir_TwoDirectories_StateChange5EdgesGraph():

    # Arrange
    graph_from_dir = create_GraphFromDirectory()
    stub_dir_walker1 = create_StubDirWalker_2DirsSimple("test1")
    stub_dir_walker2 = create_StubDirWalker_3DirsHierachy("test2")

    # Act
    graph_from_dir.set_dir_walker(stub_dir_walker1)
    graph_from_dir.add_dir("a\\b\\test1", [])

    graph_from_dir.set_dir_walker(stub_dir_walker2)
    graph_from_dir.add_dir("a\\b\\test2", [])

    # Assert
    edges, nodes = graph_from_dir.get_graph()
    assert nodes["root"]["name"] == "root"
    assert edges == {
        "node_0": {"node_1"},
        "node_2": {"node_3"},
        "node_3": {"node_4"},
        "root": {"node_0", "node_2"},
    }
    assert nodes == {
        "node_0": {"name": "test1", "path": "a\\b\\test1", "rank": 1},
        "node_1": {"name": "dir1", "path": "a\\b\\test1\\dir1", "rank": 2},
        "node_2": {"name": "test2", "path": "a\\b\\test2", "rank": 1},
        "node_3": {"name": "dir1", "path": "a\\b\\test2\\dir1", "rank": 2},
        "node_4": {"name": "dir2", "path": "a\\b\\test2\\dir1\\dir2", "rank": 3},
        "root": {"name": "root", "path": ".\\", "rank": 0},
    }


def test_traverse_dir_graph_dfs_SimpleGraph_CallsCallbackInRightOrder():
    edges = {"root": {"node_0", "node_1"}, "node_0": {"node_3"}}
    nodes = {"node_0": {}, "node_1": {}, "node_2": {}, "node_3": {}, "root": {}}

    mock_callback = MagicMock()
    mock_callback.return_value = {}
    traverse_dirgraph_dfs(edges, nodes, mock_callback)

    mock_callback.assert_has_calls(
        [
            call("root", {}),
            call("node_0", {}),
            call("node_3", {}),
            call("node_1", {}),
        ],
        any_order=False,
    )
