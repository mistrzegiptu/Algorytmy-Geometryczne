from queue import PriorityQueue
from sortedcontainers import SortedList, SortedSet
from functools import partial

class Section:
    sweepX = -float('inf')

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.a = (y1 - y2) / (x1 - x2)
        self.b = y1 - self.a * x1

    def __gt__(self, other):
        return self.a * Section.sweepX + self.b > other.a * Section.sweepX + other.b

    def __eq__(self, other):
        return self.x1 == other.x1 and self.y1 == other.y1 and self.x2 == other.x2 and self.y2 == other.y2

    def __hash__(self):
        return hash((self.x1, self.y1, self.x2, self.y2))


def ccw(a, b, c):
    det = (a[0] - c[0]) * (b[1] - c[1]) - (a[1] - c[1]) * (b[0] - c[0])
    if det > 0:
        return 1
    elif det < 0:
        return -1
    return 0

def intersect(line1, line2):
    a, b = line1
    c, d = line2
    return ccw(a, b, c) != ccw(a, b, d) and ccw(c, d, a) != ccw(c, d, b)

def instersectsObject(section1, section2):
    a, b = (section1.x1, section1.y1), (section1.x2, section1.y2)
    c, d = (section2.x1, section2.y1), (section2.x2, section2.y2)

    return ccw(a, b, c) != ccw(a, b, d) and ccw(c, d, a) != ccw(c, d, b)


def calculateIntersectingPoint(line1, line2):
    x1, y1, x2, y2 = line1.x1, line1.y1, line1.x2, line1.y2
    x3, y3, x4, y4 = line2.x1, line2.y1, line2.x2, line2.y2

    a1 = line1.a
    b1 = line1.b

    a2 = line2.a
    b2 = line2.b

    if a1 == a2:
        return None

    x = (b2 - b1) / (a1 - a2)

    if max(x1, x3) < x < min(x2, x4):
        y = a2 * x + b2
        return (x, y)

    return None

def add_intersection_event(p, index1, index2, events, processed_intersections):
    if p not in processed_intersections:
        processed_intersections.add(p)
        events.put((p, 'i', index1, index2))

def y_at_x(section, x):
    (x1, y1), (x2, y2) = section
    if x1 == x2:  # Vertical line
        return y1  # Either y1 or y2; they are the same
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)


from sortedcontainers import SortedSet


def find_intersections(sections):
    events = PriorityQueue()
    sectionObjects = []

    for i, ((x1, y1), (x2, y2)) in enumerate(sections):
        section = Section(x1, y1, x2, y2)
        sectionObjects.append(section)
        events.put(((section.x1, section.y1), 'start', i))
        events.put(((section.x2, section.y2), 'end', i))

    active = SortedList()
    intersections = SortedSet()
    processed_intersections = set()

    while not events.empty():
        event = events.get()
        point, event_type = event[:2]

        if event_type == 'start':
            index = event[2]
            Section.sweepX = point[0]
            active.add((sectionObjects[index], index))
            idx = active.index((sectionObjects[index], index))

            if idx > 0:
                neighbor = active[idx - 1][1]
                if instersectsObject(sectionObjects[neighbor], sectionObjects[index]):
                    p = calculateIntersectingPoint(sectionObjects[neighbor], sectionObjects[index])
                    if p:
                        add_intersection_event(p, neighbor, index, events, processed_intersections)
            if idx < len(active) - 1:
                neighbor = active[idx + 1][1]
                if instersectsObject(sectionObjects[neighbor], sectionObjects[index]):
                    p = calculateIntersectingPoint(sectionObjects[neighbor], sectionObjects[index])
                    if p:
                        add_intersection_event(p, index, neighbor, events, processed_intersections)

        elif event_type == 'end':
            index = event[2]
            idx = active.index((sectionObjects[index], index))
            Section.sweepX = point[0]

            neighbors = []
            if idx > 0:
                neighbors.append(active[idx - 1][1])
            if idx < len(active) - 1:
                neighbors.append(active[idx + 1][1])

            active.pop(idx)

            if len(neighbors) == 2:
                if instersectsObject(sectionObjects[neighbors[0]], sectionObjects[neighbors[1]]):
                    p = calculateIntersectingPoint(sectionObjects[neighbors[0]], sectionObjects[neighbors[1]])
                    if p:
                        add_intersection_event(p, neighbors[0], neighbors[1], events, processed_intersections)

        elif event_type == 'i':
            index1, index2 = event[2], event[3]
            intersections.add((min(index1, index2), max(index1, index2)))

            idx1 = active.index((sectionObjects[index1], index1))
            idx2 = active.index((sectionObjects[index2], index2))

            if idx1 > 0:
                neighbor = active[idx1 - 1][1]
                first, second = min(index2, neighbor), max(index2, neighbor)
                if instersectsObject(sectionObjects[first], sectionObjects[second]):
                    p = calculateIntersectingPoint(sectionObjects[first], sectionObjects[second])
                    if p:
                        add_intersection_event(p, first, second, events, processed_intersections)
            if idx1 < len(active) - 1:
                neighbor = active[idx1 + 1][1]
                first, second = min(index2, neighbor), max(index2, neighbor)
                if instersectsObject(sectionObjects[first], sectionObjects[second]):
                    p = calculateIntersectingPoint(sectionObjects[first], sectionObjects[second])
                    if p:
                        add_intersection_event(p, first, second, events, processed_intersections)
            if idx2 > 0:
                neighbor = active[idx2 - 1][1]
                first, second = min(index1, neighbor), max(index1, neighbor)
                if instersectsObject(sectionObjects[first], sectionObjects[second]):
                    p = calculateIntersectingPoint(sectionObjects[first], sectionObjects[second])
                    if p:
                        add_intersection_event(p, first, second, events, processed_intersections)
            if idx2 < len(active) - 1:
                neighbor = active[idx2 + 1][1]
                first, second = min(index1, neighbor), max(index1, neighbor)
                if instersectsObject(sectionObjects[first], sectionObjects[second]):
                    p = calculateIntersectingPoint(sectionObjects[first], sectionObjects[second])
                    if p:
                        add_intersection_event(p, first, second, events, processed_intersections)

            if idx1 > idx2:
                del active[idx1]
                del active[idx2]
            else:
                del active[idx2]
                del active[idx1]
            Section.sweepX = point[0] + 10 ** (-8)
            active.add((sectionObjects[index1], index1))
            active.add((sectionObjects[index2], index2))

    result = []
    for (i, j) in intersections:
        result.append((calculateIntersectingPoint(sectionObjects[i], sectionObjects[j]), i, j))

    return result



sections_five=[((-0.04271371103102162, 0.007908498446146661), (0.004302418001236444, -0.03691380547542198)),
((-0.03384274328908614, 0.02509599844614667), (0.017165321227042896, -0.02848856037738276)),
((-0.011000001353602261, -0.017367236847970993), (0.030915321227042908, -0.015345178024441575)),
((0.002528224452849351, -0.03185865841659845), (0.02670161154962354, 0.0031903611912447033))]

sections_six=[
    ((-0.034729840063279685, 0.019299425704806472), (0.030693547033494514, -0.03327410370695825)),
((-0.02962903361166678, -0.03563317233440923), (0.03379838574317193, 0.028735700214610402)),
((0.01117741800123645, 0.031431778645982955), (0.012064514775429996, -0.032937093903036674)),
((0.02226612767865581, 0.028061680606767267), (0.022709676065752582, -0.03394812331480138)),
((-0.024306452966505486, -0.015412584099115098), (-0.017431452966505487, -0.007661358608919019))
]

inter = find_intersections(sections_six)
print(inter)