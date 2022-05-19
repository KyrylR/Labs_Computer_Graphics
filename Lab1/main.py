import math

from matplotlib import patches, pyplot as plt

print([1, 2, 3, 4, 5][2:])


def read_data_from_file(filepath: str):
    """
    Getting data with a list of points, as well as
    search points - points that define the search area

    :param filepath: path to data file
    :return: Tuple of: points list and search list
    """
    try:
        with open(filepath, mode='r+') as data_file:
            init_val = False
            points_quantity, counter = -1, 0
            points_list = []
            search_list = []
            for line in data_file:
                if not line.startswith("#"):
                    if not init_val:
                        points_quantity = int(line.strip())
                        init_val = True
                        continue
                    if counter < points_quantity:
                        value_list = list(map(int, line.split(" ")))
                        points_list.append(Point(value_list[0], value_list[1]))
                        counter += 1
                        continue
                    value_list = list(map(int, line.split()))
                    search_list.append(Point(value_list[0], value_list[1]))

            return points_list, search_list
    except FileNotFoundError as err:
        print('File do not exist')
        raise err
    except IOError as err:
        print('IO error')
        raise err


class Point:
    """
    Default class of points with all interrelation
    operations for x and y, separately and for both
    """
    __slots__ = ['x', 'y']

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def grater_only_x(self, other):
        return self.x > other.x

    def grater_only_y(self, other):
        return self.y > other.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __gt__(self, other):
        return self.x > other.x and self.y > other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y > other.y

    def __lt__(self, other):
        return not (self.__gt__(other))

    def __le__(self, other):
        return not (self.__ge__(other))

    def __ne__(self, other):
        return not (self.__eq__(other))

    def __str__(self):
        return "(%d,%d)" % (self.x, self.y)

    def __repr__(self):
        return "(%d,%d)" % (self.x, self.y)


class NodeData:
    __slots__ = ['left_index', 'right_index', 'sorted_y']

    def __init__(self, left: int, right: int, sorted_y: list):
        self.left_index = left
        self.right_index = right
        self.sorted_y = sorted_y

    def __repr__(self):
        return f"[{self.left_index}; {self.right_index}), {self.sorted_y}"


class Node:
    __slots__ = ['data', 'left', 'right']

    def __init__(self, data: NodeData = None, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.data}"

    def graph_viz(self, string_mutable):
        if self is None:
            return

        string_mutable[0] += f"\"{self}\"\n"

        if self.left is not None:
            string_mutable[0] += f"\"{self}\" -> \"{self.left}\" [label = \"left\"]\n"
        if self.right is not None:
            string_mutable[0] += f"\"{self}\" -> \"{self.right}\" [label = \"right\"]\n"

        if self.left is not None:
            self.left.graph_viz(string_mutable)

        if self.right is not None:
            self.right.graph_viz(string_mutable)


def sort_by_y(to_sort: list):
    return sorted(to_sort, key=lambda points: points.y)


def check_axis_y(to_check_y, down, up) -> bool:
    return down <= to_check_y <= up


class SegmentTree:
    """
    Build segment tree of given points of type Point.
    """
    __slots__ = ['root', 'x_cords', 'y_cords', 'result']

    def __init__(self, points_list: list, search_area: list):
        point_list.sort(key=lambda point: point.x)
        self.root = self.build_tree(points_list, points_list[0].x, points_list[-1].x)
        self.x_cords = (min(search_area[0].x, search_area[1].x), max(search_area[0].x, search_area[1].x))
        self.y_cords = (min(search_area[0].y, search_area[1].y), max(search_area[0].y, search_area[1].y))
        self.result = []

    def build_tree(self, points_list: list, left_index, right_index) -> Node:
        if len(points_list) == 1:
            return Node(NodeData(points_list[0].x, points_list[-1].x + 1, points_list), None, None)
        median = math.floor((1 + len(points_list)) / 2)
        left_list = points_list[:median]
        left = self.build_tree(left_list, points_list[0].x, points_list[-1].x)
        median = math.floor((1 + len(points_list)) / 2)
        right_list = points_list[median:]
        right = self.build_tree(right_list, points_list[0].x, points_list[-1].x)
        return Node(NodeData(points_list[0].x, points_list[-1].x + 1, sort_by_y(points_list)), left, right)

    def graph_viz(self):
        string = "digraph g {\n"
        wrapper = [string]

        self.root.graph_viz(wrapper)
        wrapper[0] += "}\n"

        with open("data/graph_viz.txt", mode='w+') as data_file:
            data_file.write(wrapper[0])

    def plot_points(self, figure, axes):
        for index, point in enumerate(self.root.data.sorted_y):
            axes.scatter([point.x], [point.y], color="red")
            axes.annotate(f"({point.x}; {point.y})", (point.x, point.y),
                          xytext=(point.x - 0.025, point.y + 0.1))

    def plot_region(self, axes, search_region):
        width = search_region[1].x - search_region[0].x
        height = search_region[1].y - search_region[0].y

        rect = patches.Rectangle((search_region[0].x, search_region[0].y), width, height, linewidth=1, edgecolor='b',
                                 facecolor='none')
        axes.add_patch(rect)

    def query(self):
        search_root = self.root
        # TODO with None
        if search_root is None:
            return

        while search_root.right.data.left_index >= self.x_cords[1]:
            search_root = search_root.left
            if search_root is None:
                return

        while search_root.left.data.right_index <= self.x_cords[0]:
            search_root = search_root.right
            if search_root is None:
                return

        self.query_left(search_root.left)
        self.query_right(search_root.right)

    def query_left(self, left_node: Node):
        if self.check_segment(left_node.right):
            self.query_left(left_node.left)

    def query_right(self, right_node: Node):
        if self.check_segment(right_node.left):
            self.query_right(right_node.right)

    def check_segment(self, node: Node):
        # Add nested segments
        res = False
        if node is None:
            return res
        if self.x_cords[0] <= node.data.left_index and self.x_cords[1] >= node.data.right_index:
            res = True
            for item in node.data.sorted_y:
                if check_axis_y(item.y, self.y_cords[0], self.y_cords[1]):
                    self.result.append(item)
        return res


if __name__ == "__main__":
    point_list, search_list = read_data_from_file("data/data.txt")
    tree = SegmentTree(point_list, search_list)
    tree.query()
    print(tree.result)
    print(tree.graph_viz())

    figure, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    tree.plot_points(figure, axes)
    tree.plot_region(axes, search_list)
    plt.show()
