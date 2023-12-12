# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
from game import Directions

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    return [
        Directions.WEST,
        Directions.WEST,
        Directions.WEST,
        Directions.WEST,
        Directions.SOUTH,
        Directions.SOUTH,
        Directions.EAST,
        Directions.SOUTH,
        Directions.SOUTH,
        Directions.WEST,
        Directions.WEST,
    ]
    # raise Exception("Lmao")


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    # raise Exception("Lmao")
    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    visited = []
    solution = util.Stack()

    def dfs_search(problem, current_node, visited, solution):
        visited.append(current_node[0])
        if problem.isGoalState(current_node[0]):
            solution.push(current_node)
            return 1

        neighbors = problem.getSuccessors(current_node[0])

        if not neighbors:
            return -1

        solution.push(current_node)
        for i in neighbors:
            if i[0] not in visited:
                status = dfs_search(problem, i, visited, solution)
                if status == -1:
                    solution.pop()

                elif status == 1:
                    return 1

        solution.pop()

    start_state = [problem.getStartState(), '', 0]

    dfs_search(problem, start_state, visited, solution)
    path = [i[1] for i in solution.list if i[1] != '']
    # print("Full maze:", visited)
    # print("Solution:", [i[0] for i in solution.list])

    return path


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    visited = []
    queue = util.Queue()
    solution = util.Queue()
    start_state = [problem.getStartState(), '', 0]

    # visited.append(start_state[0])
    queue.push(start_state)

    def bfs_search(problem, queue, solution, path):
        if queue.isEmpty():
            return path

        current_node = queue.pop()
        visited.append(current_node[0])
        if problem.isGoalState(current_node[0]):
            return path

        neighbors = problem.getSuccessors(current_node[0])
        # print(neighbors)

        for i in neighbors:
            if i[0] not in visited:
                queue.push(i)
                solution.push(path + [i])

        return bfs_search(problem, queue, solution, solution.pop())

    thingy = bfs_search(problem, queue, solution, [])

    moves = [i[1] for i in thingy if i[1] != '']
    return moves

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    visited = []
    queue = util.PriorityQueue()
    solution = util.PriorityQueue()
    start_state = [problem.getStartState(), '', 0]

    visited.append(start_state[0])
    queue.push(start_state, 0)

    move_dict = {
        'South': Directions.SOUTH,
        'North': Directions.NORTH,
        'East': Directions.EAST,
        'West': Directions.WEST,
    }

    path = []
    while queue.heap:
        current_node = queue.pop()
        if problem.isGoalState(current_node[0]):
            break

        neighbors = problem.getSuccessors(current_node[0])

        for i in neighbors:
            if i[0] not in visited:
                visited.append(i[0])
                path_temp = path + [i]
                moves = [move_dict[i[1]] for i in path_temp]
                cost = problem.getCostOfActions(moves)

                queue.push(i, cost)
                solution.push(path_temp, cost)

        path = solution.pop()

    paths = [move_dict[i[1]] for i in path]
    print(paths)

    return paths
    # raise Exception("Lmao")


def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    raise Exception("Lmao")


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
