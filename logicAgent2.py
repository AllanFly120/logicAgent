import copy
input_path = './sample05_6.txt'
output_path = './log.txt'

# to transfer the string indicating the arguments, like 'x, y, z', into a list of x y z
def get_variable(string):
    rtn = []
    string_list = string.split(', ')
    for substr in string_list:
        rtn.append(substr)
    return rtn


def parse_sentence(string):
    rtn = Sentence()
    if string.find(' => ') is not -1:
        left = string[0:string.find(' => ')]
        right = string[string.find(' => ')+4:]
        left_list = left.split(" && ")
        for substr in left_list:
            predicate = substr[0:substr.find('(')]
            variables = substr[substr.find('(') + 1:substr.find(')')]
            variable_list = get_variable(variables)
            left_atomic = Atomic(predicate, variable_list)
            rtn.append_on_left(left_atomic)
        predicate = right[0:right.find('(')]
        variables = right[right.find('(') + 1:right.find(')')]
        variable_list = get_variable(variables)
        right_atomic = Atomic(predicate, variable_list)
        rtn.append_on_right(right_atomic)
    else:
        predicate = string[0:string.find('(')]
        variables = string[string.find('(') + 1:string.find(')')]
        variable_list = get_variable(variables)
        atomic = Atomic(predicate, variable_list)
        rtn.append_on_right(atomic)

    return rtn


def get_query(input_path):
    fh = open(input_path, 'r')
    for i, line in enumerate(fh.readlines()):
        if i == 0:
            string_list = line.split(' && ')
            query = Sentence()
            for substring in string_list:
                predicate = substring[0:substring.find('(')]
                variables = substring[substring.find('(') + 1:substring.find(')')]
                variable_list = get_variable(variables)
                query_atomic = Atomic(predicate, variable_list)
                query.append_on_right(query_atomic)
        else:
            break
    return query


def split_query(query):
    for query_atomic in query.rhs:
        splitted = Sentence()
        splitted.append_on_right(query_atomic)
        yield splitted


def is_variable(argument):
    if argument[0].islower():
        return True
    else:
        return False


def is_constant(argument):
    if argument[0].isupper():
        return True
    else:
        return False


def print_log(atomic, theta=None):
    log_writer.write(atomic.predicate)
    log_writer.write('(')
    for i, argument in enumerate(atomic.argument_list):
        # if is_variable(argument) and theta is not None and argument in theta:
        #     log_writer.write(theta[argument])
        # elif is_variable(argument):
        #     log_writer.write('_')
        # else:
        #     log_writer.write(argument)
        log_writer.write(argument)
        if i is not len(atomic.argument_list) - 1:
            log_writer.write(', ')
    log_writer.write(')\n')


def get_usable_letters(letter_set, sentence):
    for left_atomic in sentence.lhs:
        for argument in left_atomic.argument_list:
            if is_variable(argument) and argument in letter_set:
                letter_set.remove(argument)
    return letter_set


def standardize_var(rule, goal, theta):
    # rule.print_content()
    variable_denote = set()
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    for letter in all_letters:
        variable_denote.add(letter)
    get_usable_letters(variable_denote, rule)
    # print(variable_denote)
    subst_dict = {}


    goal_arguments = goal.rhs[0].argument_list
    rule_rhs_arguments = rule.rhs[0].argument_list

    for i, argument in enumerate(goal_arguments):
        if is_variable(argument) and is_variable(rule_rhs_arguments[i]) and argument is not rule_rhs_arguments[i]:
            subst_dict[rule_rhs_arguments[i]] = argument
        if is_variable(rule_rhs_arguments[i]) and is_constant(argument) and rule_rhs_arguments[i] in theta and not rule_rhs_arguments[i] in subst_dict:
            subst_dict[rule_rhs_arguments[i]] = variable_denote.pop()
    # print(subst_dict)

    for rule_lhs_atomic in rule.lhs:
        for i, argument in enumerate(rule_lhs_atomic.argument_list):
            if is_variable(argument) and argument in subst_dict.keys():
                del rule_lhs_atomic.argument_list[i]
                rule_lhs_atomic.argument_list.insert(i, subst_dict[argument])
            elif is_variable(argument) and argument in subst_dict.values():
                subst_dict[argument] = variable_denote.pop()  #pop() need to check whether the set is empty
                del rule_lhs_atomic.argument_list[i]
                rule_lhs_atomic.argument_list.insert(i, subst_dict[argument])

    for rule_rhs_atomic in rule.rhs:
        for i, argument in enumerate(rule_rhs_atomic.argument_list):
            if is_variable(argument) and argument in subst_dict.keys():
                del rule_rhs_atomic.argument_list[i]
                rule_rhs_atomic.argument_list.insert(i, subst_dict[argument])
            elif is_variable(argument) and argument in subst_dict.values():
                subst_dict[argument] = variable_denote.pop()  #pop() need to check whether the set is empty
                del rule_rhs_atomic.argument_list[i]
                rule_rhs_atomic.argument_list.insert(i, subst_dict[argument])

    # rule.print_content()
    return rule


def unify_var(rule, goal, theta):
    # if rule in theta:
    #     return unify(theta[rule], goal, theta)
    # if goal in theta:
    #     return unify(rule, theta[goal], theta)
    # else:
    #     theta_a = copy.deepcopy(theta)
    #     theta_a[rule] = goal
    #     return theta_a
    # print(theta)
    theta_a = copy.deepcopy(theta)
    theta_a[rule] = goal
    # print(theta_a)
    return theta_a

# goal_predicate = ''


def unify(rule, goal, theta):
    if theta is None:
        return None

    elif rule == goal:
        return theta

    elif isinstance(rule, str) and is_variable(rule):
        return unify_var(rule, goal, theta)

    elif isinstance(goal, str) and is_variable(goal):
        return unify_var(goal, rule, theta)

    elif isinstance(rule, Atomic) and isinstance(goal, Atomic):
        global goal_predicate
        goal_predicate = goal.predicate
        return unify(rule.argument_list, goal.argument_list, unify(rule.predicate, goal.predicate, theta))

    elif isinstance(rule, list) and isinstance(goal, list):
        return unify(rule[1:], goal[1:], unify(rule[0], goal[0], theta))

    else:
        return None


def subst(theta, first):
    rtn = Sentence()
    for first_atomic in first:
        for i, first_atomic_argument in enumerate(first_atomic.argument_list):
            if first_atomic_argument in theta.keys():
                first_atomic.argument_list[i] = theta[first_atomic_argument]
        rtn.append_on_right(copy.deepcopy(first_atomic))
    return rtn


def bw_chaining(kb, query):
    theta = {}
    depth = 0
    return bw_or(kb, query, theta)


def list_print(list):
    for i in list:
        i.print_content()


def bw_or(kb, goal, theta):
    list = kb.fetch_rules(goal, theta)
    print(theta)
    if len(list) is 0:
        log_writer.write('Ask: ')
        print_log(goal.rhs[0], theta)
        log_writer.write('False: ')
        print_log(goal.rhs[0], theta)
    for i, rule in enumerate(list):
        log_writer.write('Ask: ')
        print_log(goal.rhs[0], theta)
        rule = standardize_var(rule, goal, theta)
        for theta_a in bw_and(kb, rule, unify(rule.rhs, goal.rhs, theta)):
            yield theta_a
            break
    # else:
    #     log_writer.write('False: ')
    #     print_log(goal.rhs[0], theta)


def bw_and(kb, goals, theta):
    if theta is None:
        # log_writer.write('False: \n')
        return

    elif len(goals.lhs) is 0:
        log_writer.write('True: ')
        print_log(goals.rhs[0], theta)
        yield theta
    else:
        tmp = copy.deepcopy(goals)
        first = []
        first.append(tmp.lhs[0])
        del tmp.lhs[0]
        rest = tmp

        for theta_a in bw_or(kb, subst(theta, first), theta):
            for theta_b in bw_and(kb, rest, theta_a):
                yield theta_b


class Atomic:
    def __init__(self, predicate, argument_list):
        self.predicate = predicate
        self.argument_list = argument_list

    def print_atomic(self):
        log_writer.write(self.predicate)
        log_writer.write('(')
        for i, argument in enumerate(self.argument_list):
            log_writer.write(argument)
            if i is not len(self.argument_list) - 1:
                log_writer.write(', ')
        log_writer.write(')')

    def atomic_to_str(self):
        s = ''
        s += self.predicate
        s += '('
        for i, argument in enumerate(self.argument_list):
            s += argument
            if i is not len(self.argument_list) - 1:
                s += ', '
        s += ')'
        return s


class Sentence:
    def __init__(self, **kwargs):
        if len(kwargs) is 0:
            self.lhs = []
            self.rhs = []
        else:
            self.lhs = []
            self.rhs = []
            if 'left' in kwargs.keys():
                self.lhs = kwargs['left']
            if 'right' in kwargs.keys():
                self.rhs = kwargs['right']


    def append_on_left(self, atomic):
        self.lhs.append(atomic)

    def append_on_right(self, atomic):
        self.rhs.append(atomic)

    def print_content(self):
        if len(self.lhs) is not 0:
            for i, atomic in enumerate(self.lhs):
                atomic.print_atomic()
                if i is not len(self.lhs) - 1:
                    log_writer.write(' && ')
            log_writer.write(' => ')
        for i, atomic in enumerate(self.rhs):
            atomic.print_atomic()
            if i is not len(self.rhs) - 1:
                log_writer.write(' && ')
        log_writer.write('\n')
    pass


def right_constant(atomic_a, atomic_b):
    a_argument_list = atomic_a.argument_list
    b_argument_list = atomic_b.argument_list
    for i, argument in enumerate(a_argument_list):
        if is_constant(argument) and is_constant(b_argument_list[i]) and b_argument_list[i] != argument:
            return False
    return True


def all_constant_argument(atomic):
    for argument in atomic.argument_list:
        if is_variable(argument):
            return False
    return True


def all_same_arguments(atomic_a, atomic_b):
    if len(atomic_a.argument_list) != len(atomic_b.argument_list):
        return False
    for i, argument in enumerate(atomic_a.argument_list):
        if atomic_b.argument_list[i] != argument:
            return False
    return True


class KB:
    def __init__(self):
        # self.fetched = []
        self.sentences = []
        fh = open(input_path)
        for i, line in enumerate(fh.readlines()):
            if i > 1:
                self.sentences.append(parse_sentence(line))
                # self.fetched.append(False)
                # parse_sentence(line).print_content()

    def fetch_rules(self, goal, theta):
        for goal_right_atomic in goal.rhs:
            goal_predicate = goal_right_atomic.predicate
        rtn = []
        for i, sentence in enumerate(self.sentences):
            sentence_predicate = sentence.rhs[0].predicate
            if sentence_predicate == goal_predicate:
                record_sentence = sentence
                if not right_constant(goal.rhs[0], sentence.rhs[0]):
                    continue
                rtn.append(sentence)
                # yield copy.deepcopy(sentence)    # may not need a deep copy
        return copy.deepcopy(rtn)

    def print_kb(self):
        for sentence in self.sentences:
            sentence.print_content()


def main():
    global log_writer
    log_writer = open(output_path, 'w')
    query = get_query(input_path)
    # query.print_content()
    kb = KB()
    # kb.print_kb()
    # standardize_var(kb.sentences[0], query)
    for splitted_query in split_query(query):
        for theta in bw_chaining(kb, splitted_query):
            break
        else:
            log_writer.close()
            fi = open(output_path)
            last = ''
            for last_line in fi.readlines():
                last = last_line
            fi.close()
            print(last)
            goal_str = 'False: ' + splitted_query.rhs[0].atomic_to_str()
            print(goal_str)
            end_writer = open('./log.txt', 'a')
            if goal_str.strip() != last.strip():
                end_writer.write(goal_str + '\n')
            end_writer.write('False')
            end_writer.close()
            return
    log_writer.write('True')

if __name__ == "__main__":
    main()

