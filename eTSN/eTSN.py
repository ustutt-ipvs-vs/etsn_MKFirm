import time

from docplex.cp.model import CpoModel
from docplex.cp.solution import CpoSolveResult

from eTSN.schedulingStructs import SchedulingParameters, CpVariables


def solve_scheduling(parameters: SchedulingParameters) -> CpoSolveResult:
    variables = CpVariables(parameters)

    mdl = CpoModel()
    # create constraints (use functions)

    # create the optimization goal (use a function)

    # call the actual planning
    result = planning(mdl, parameters)

    return result


def planning(mdl: CpoModel, param: SchedulingParameters) -> CpoSolveResult:
    start_solving_time = time.time()

    if param.verbose:
        print("Solving model....")
    log_verbosity = 'Quiet' if param.raw_output else 'Terse'
    warning_level = 0 if param.raw_output else 2
    mdl_sol: CpoSolveResult
    if param.cplex_executable:
        mdl_sol = mdl.solve(TimeLimit=param.timeout, Workers=param.threads, LogVerbosity=log_verbosity,
                            WarningLevel=warning_level,
                            execfile=param.cplex_executable)
    else:
        mdl_sol = mdl.solve(TimeLimit=param.timeout, Workers=param.threads, WarningLevel=warning_level,
                            LogVerbosity=log_verbosity)

    end_solving_time = time.time()

    if param.verbose:
        mdl_sol.print_solution()
        print("Solving time: ", end_solving_time - start_solving_time)

    return mdl_sol
