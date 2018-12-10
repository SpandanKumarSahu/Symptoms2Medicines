from __future__ import print_function
from pyddl import Domain, Problem, Action, neg, planner
from string import punctuation

def problem(verbose):
    with open("all_data.csv", "r") as f:
        data = f.readlines()
        data = [x.strip().strip(punctuation) for x in data]
    data = data[:40]
    medicines = []
    symptoms = []
    domain = Domain((
        Action(
            'take',
            parameters = (
                ('medicine', 'med'),
                ('symptom', 'sym1'),
                ('symptom', 'sym2'),
                ('symptom', 'sym3'),
            ),
            preconditions = (
                ('cures', 'med', 'sym1'),
                ('cures', 'med', 'sym2'),
                ('cures', 'med', 'sym3'),
                ('have_med', 'med'),
                ('has', 'sym1'),
                ('has', 'sym2'),
                ('has', 'sym3'),
            ),
            effects = (
                ('had', 'sym1'),
                ('had', 'sym2'),
                ('had', 'sym3'),
                neg(('have_med', 'med')),
            ),
        ),
    ))
    user_init = []
    user_goal = []
    user_symptoms = []

    for x in data:
        y = x.split(',')
        y = [z.strip(punctuation) for z in y]
        if len(y) < 2 or len(y) > 4:
            continue
        medicines.append(y[0])
        user_init.append(('have_med', str(y[0])))
        symptoms += y[1:]
        for sym in y[1:]:
            user_init.append(('cures', str(y[0]), str(sym)))

    with open("user_symptoms.txt", "r") as f:
        syms = f.readlines()
        syms = [s.strip().strip(punctuation) for s in syms]
        for sym in syms:
            user_init.append(('has', str(sym)))
            user_symptoms.append(str(sym))
            user_goal.append(('had', str(sym)))

    total_symptoms = len(user_init)
    user_symptoms = list(set(user_symptoms))

    problem = Problem(
        domain,
        {
            'medicine': list(set(medicines)),
            'symptom': list(set(symptoms)),
        },
        init=user_init,
        goal=user_goal,
    )

    def distance_heuristic(state):
        num_satisfied = len([p for p in state.predicates if p[0] == "had" and p[1] in user_symptoms])
        return total_symptoms - num_satisfied

    plan = planner(problem, heuristic=distance_heuristic, verbose=verbose)
    if plan is None:
        print('No Plan!')
    else:
        for action in plan:
            print(action)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option('-q', '--quiet',
                      action='store_false', dest='verbose', default=True,
                      help="don't print statistics to stdout")
    # Parse arguments
    opts, args = parser.parse_args()
    problem(opts.verbose)
