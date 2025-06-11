"""A class to hold candidate base concepts in set refactoring process"""

"""This is taken from JC's pre NHS work"""


class CandidateBaseConcept:
    def __init__(
        self, concept_id=None, concepts=None, target_members=None, must_avoid_set=None
    ):
        self.concept_id = concept_id
        self.concept = concepts[concept_id]
        self.concepts = concepts
        self.target_members = target_members
        self.score = -999

        # avoid this:    self.desc_plus_self=copy.deepcopy(self.concept.descendants)
        # takes ages for root concept etc
        self.is_in_membership = concept_id in self.target_members

        self.n_desc_plus_self_all = (
            len(self.concept.descendants) + 1
        )  # this seems in line with definition of NUMDESCENDENTS
        self.n_desc_plus_self_in_membership = len(
            self.concept.descendants.intersection(self.target_members)
        )
        if self.is_in_membership:
            self.n_desc_plus_self_in_membership += (
                1  # this seems lin line with definition of TRUEPOS
            )
        self.n_desc_plus_self_not_in_membership = (
            self.n_desc_plus_self_all - self.n_desc_plus_self_in_membership
        )  # this seesm in line wiht definitions of TRUENEG

        if must_avoid_set is not None:
            self.valset_members_hit = self.concept.descendants.intersection(
                must_avoid_set
            )
            # print(len(must_avoid_set))

        if self.is_in_membership:
            self.operator = "<<"
        else:
            self.operator = "<"

        if must_avoid_set is not None:
            self.is_perfect_fit = self.concept.descendants.isdisjoint(must_avoid_set)
        else:
            if self.is_in_membership:
                self.is_perfect_fit = self.n_desc_plus_self_not_in_membership == 0
            else:
                self.is_perfect_fit = (
                    self.n_desc_plus_self_not_in_membership == 1
                )  # with "<" operator self will be ignored

        self.clause_string = self.operator + str(self.concept_id)

        self.n_children_all = len(self.concept.children)
        self.n_children_in_membership = len(
            set(self.concept.children).intersection(self.target_members)
        )

    def __str__(self):
        str_str = "\nCandidateBaseConcept:\n-------------\n"
        str_str += "concept_id: %s\n" % self.concept_id
        str_str += "pt: %s\n" % self.concepts[self.concept_id].pt
        str_str += "is_in_membership: %s\n" % self.is_in_membership
        str_str += "is_perfect_fit: %s\n" % self.is_perfect_fit
        str_str += "clause_string: %s\n" % self.clause_string
        str_str += "n_desc_plus_self_all: %s\n" % self.n_desc_plus_self_all
        str_str += (
            "n_desc_plus_self_in_membership: %s\n" % self.n_desc_plus_self_in_membership
        )
        str_str += (
            "n_desc_plus_self_not_in_membership: %s\n"
            % self.n_desc_plus_self_not_in_membership
        )
        str_str += "n_children_all: %s\n" % self.n_children_all
        str_str += "n_children_in_membership: %s\n" % self.n_children_in_membership
        return str_str

    def set_score(self, *, zoom=None, verbose=False):
        self.score = self.n_desc_plus_self_in_membership / self.n_desc_plus_self_all
        if not self.is_in_membership:
            self.score = self.score * 0.95
        if self.score < 0.7:
            if verbose:
                print(
                    float(len(self.target_members)),
                    self.n_desc_plus_self_in_membership,
                    float(len(self.target_members))
                    / self.n_desc_plus_self_in_membership,
                )

            self.score = self.score * (
                1.0
                / (
                    abs(
                        (
                            float(len(self.target_members))
                            / self.n_desc_plus_self_in_membership
                        )
                        - zoom
                    )
                    + 1
                )
            )
