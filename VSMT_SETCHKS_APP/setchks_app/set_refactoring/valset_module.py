""" module for holding value sets as Valsets and Clauses"""
import re
import sys

"""
This module originated from JC's personal pre NHS work where it was focused on SNOMED refsets
The nomenclature has been generalised to reflect appliation to any SNOMED value set
The handling (e.g. of membership analysis is all based on having access to "descendant" and "ancestor" lists 
for every concept and is not based on using a FHIR terminology server. For some operations calling for such
lists via ECL to a term server seems too slow.

The name valset is used to distinguish from the FHIR ValueSet or value_set.

Some of the handling (e.g. of ValsetCollection) was based on handling large collections of refsets
so is perhaps a bit clumsy for some of the current refactoring application
"""


class Clause():

    def __init__(self, clause_string=None):
        
        #trim off brackets
        if clause_string[0]=="[": 
            clause_string=clause_string[1:]
        if clause_string[-1]=="]": 
            clause_string=clause_string[:-1]
        # print(clause_string[0:2], clause_string[0:2]=="@-")

        # trim off "@" *indicates stickiness against refactoring I think
        if clause_string[0]=="@":
            clause_string=clause_string[1:]
            self.sticky=True # in DMWB this means clause will not be lost or refactored even if apparently not achieveing anything
        else:
            self.sticky=False

        #check if exclusion and trim if necessary
        if clause_string[0:1]=="-":
            clause_string=clause_string[1:]
            clause_type="exclude"   
        else:
            clause_type="include"

        self.clause_string=clause_string
        self.clause_type=clause_type
        
        mObj=re.search(r'([^0-9\-]*)([0-9\-]*)$',self.clause_string) # \- minus is to cope with -9999 as the dummy_inactive_concept

        
        self.clause_operator=mObj.groups()[0]
        #STOPGAP UNTIL CHECK - SET BLANK OPERATOR TO "="
        if self.clause_operator=="":
            print("WARNING: AS STOPGAP MEASURE setting blank operator to '=' in %s" % clause_string)
            self.clause_operator="="

        self.clause_base_concept_id=int(mObj.groups()[1])
       

    def __repr__(self):
        return str(self.__dict__.items())



class ClauseMembershipAnalysis():   # one Clause could have one of these 
                                    # for each relevant branch being anaysed

    def __init__(self, clause=None, concepts=None, branch_label=""):
        # the concepts dictionary "defines" the branch
        # the branch label is optional to help keep track of branch specific info
        self.clause=clause
        self.branch_label=branch_label

        #for ontoserver style need to force concept to be looked for
        # print("==>>>", clause)

        # if clause.clause_base_concept_id not in concepts:
        #     dummy=concepts[clause.clause_base_concept_id]
        #     print("Fetched dummy")
        #     print(dummy)

        # if clause.clause_base_concept_id in concepts:
        concept=concepts[clause.clause_base_concept_id]
        # print("Got the base concept")
        if concept is not None:
            if clause.clause_operator=="=":
                self.members=[concept.concept_id]
                self.depth=-1 # recursive view should only ever show self
            elif clause.clause_operator=="<":
                #dummy2=concept.descendants # for ontoserver vsn
                #print(dummy2)
                self.members=list(concept.descendants)
                self.depth=99999 # recursive view should go as deep as likes
            elif clause.clause_operator=="<<":
                #dummy2=concept.descendants # for ontoserver vsn
                self.members=[concept.concept_id]+list(concept.descendants)
                self.depth=99999 # recursive view should go as deep as likes
            elif clause.clause_operator==":=":
                self.members=list(concept.modelled_relns_as_destination.keys())
                self.depth=-9999 # recursive view should currently not show it
            elif clause.clause_operator==":<":
                self.members=[]
                for descendant_concept_id in [concept.concept_id]+list(concept.descendants):
                    self.members+=list(concepts[descendant_concept_id].modelled_relns_as_destination.keys())
                self.depth=-9999 # recursive view should currently not show it
            else:
                print("Illegal operator ==>%s<== %s" % (clause.clause_operator, clause))
                sys.exit()
            self.n_members=len(self.members)
        else:
            self.members=[]
            self.n_members=0
            self.depth=-1

        #
        # Analyse the number of each semantic tag in the clause membership
        #

        # print("MEMBERS",self.members)
        self.semantic_tag_counts={}
        # for concept_id in self.members:
        #     semantic_tag=concepts[concept_id].semantic_tag
        #     if semantic_tag not in self.semantic_tag_counts:
        #         self.semantic_tag_counts[semantic_tag]=0
        #     self.semantic_tag_counts[semantic_tag]+=1

   
class ClauseBasedRule():

    def __init__(self, clause_set_string=None):
        self.clause_set_string=clause_set_string
        self.clauses=[]
        for clause_string in self.clause_set_string.split('|'):
            if clause_string: # lose blank clauses
                self.clauses.append(Clause(clause_string=clause_string.strip()))

    def __repr__(self):
        repr_strings=[]
        repr_strings.append("ClauseBasedRule:")
        repr_strings.append("Defining string: " + self.clause_set_string)
        repr_strings.append("Clauses: "+str(self.clauses))
        return "\n".join(repr_strings)

    # def get_base_concepts_info(self, snowstorm_connection): # do this for whole clause set in one go to reduce snowstorm API calls (i.e. for speed)
    #     ids=[clause.clause_base_concept_id for clause in self.clauses]
    #     concept_list=snowstorm_connection.get_concepts_by_id(ids)
    #     fsn_dict={}
    #     for item in concept_list["items"]:
    #         fsn_dict[item["conceptId"]]=item["fsn"]["term"]
    #     for clause in self.clauses:
    #         if clause.clause_base_concept_id in fsn_dict.keys():
    #             clause.clause_base_concept_validity=True
    #             clause.clause_base_concept_fsn=fsn_dict[clause.clause_base_concept_id]
    #         else:
    #             clause.clause_base_concept_validity=False
    #             clause.clause_base_concept_fsn="NOT IN THIS BRANCH"
        
class ValsetCollection(list):
    def __init__(self):
        self.global_exclusions=None
        self.valset_name_to_id={}
        # self.create_filter_valsets()
    def append(self, valset=None):
        self.valset_name_to_id[valset.valset_name]=len(self) # keep a map of names in the list
        if valset.valset_collection is None: 
            valset.valset_collection=self   # this will allow a valset to retrieve e.g. the filter_memberships,
                                            # which are common to all valsets in collection,
                                            # even though their application is controlled by valset level flags
        else:
            print("======> Error, valset is already in a collection")
            print(valset)
            sys.exit()
        super().append(valset)

    # def process_filters(self, concepts=None): # NEED TO THINK WHAT HAPPENS IF have more than one set of concepts in play
    #     print("In process_filters")
    #     self.filter_memberships={}
    #     for filter in ["GLOBEX","EXCLUDE_LINKAGE_ET_AL","EXCLUDE_INACTIVE_ET_AL","EXCLUDE_CLINICALLY_UNLIKELY","EXCLUDE_DRUGS_ET_AL"]:
    #         valset_id=self.valset_name_to_id[filter]
    #         self.filter_memberships[filter]=ValsetMembershipAnalysis(valset=self[valset_id], 
    #                                                                 concepts=concepts, 
    #                                                                 global_exclusions=[], 
    #                                                                 stub_out_interaction_matrix_calc=True).final_inclusion_list
    #         print("Filter", filter, "contains", len(self.filter_memberships[filter]))

    # def create_filter_valsets(self):
    #     exclusion_filters={
    #     "EXCLUDE_LINKAGE_ET_AL": "<<106237007 | <<370136006 | <<900000000000441003",
    #     #"EXCLUDE_INACTIVE_ET_AL": "<<362955004 | <<363743006",
    #     "EXCLUDE_INACTIVE_ET_AL": "<<-9999 | <<363743006",    # -9999 is a dummy concept that has all inactive concepts as its descendants
    #     "EXCLUDE_CLINICALLY_UNLIKELY": "<<123037004 | <<308916002 | <<410607006 | <<78621006 | <<260787004 | <<362981000 | <<419891008 | <<123038009 | <<254291000",
    #     "EXCLUDE_DRUGS_ET_AL": "<<105590001 | <<373873005",
    #     }
        # for filter_name, filter_sctrule in exclusion_filters.items():
        #     self.append(Valset(valset_name=filter_name, valset_description=filter_name, clause_set_string=filter_sctrule, metadata_column=None, is_a_filter_valset=True))
        #     valset_id=self.valset_name_to_id[filter_name]
        #     print("TESTING=====================>", self[valset_id])


class Valset():
    __slots__=[
        "valset_name",
        "valset_description",
        "clause_set_string",
        "clause_based_rule",
        "metadata_column",
        "is_a_filter_valset",
        "valset_collection",
        "export_filter",
        "lexical_filter",
        "filter_flags",
        "apply_filters",     
    ]
    def __init__(
        self, 
        valset_name=None, 
        valset_description=None, 
        clause_set_string=None, 
        valset_extens_defn=None, 
        metadata_column=None, 
        is_a_filter_valset=False,
        ):
        self.valset_name=valset_name
        self.valset_description=valset_description
        self.clause_set_string=clause_set_string
        #quick workround to allow extensional definition 
        if valset_extens_defn!=None:
            if valset_extens_defn!=set():
                valset_extens_defn=[str(x) for x in valset_extens_defn] # make sure all strings
                self.clause_set_string="=" +"|=".join(valset_extens_defn)
            else:
                self.clause_set_string="" # otherwise empty set generate "=" which causes int() error below
                                          # need to still test to see what happens if give refactoring an empy clause_set_string
        self.clause_based_rule=ClauseBasedRule(clause_set_string=self.clause_set_string)

        self.metadata_column=metadata_column
        self.is_a_filter_valset=is_a_filter_valset
        self.valset_collection=None # this is set by the ValsetColection append method
        self.process_metadata()
        
    def __repr__(self):
        repr_strings=[]
        repr_strings.append("ValSet:")
        repr_strings.append("Name: " + str(self.valset_name))
        if self.is_a_filter_valset:
            repr_strings.append("This is a filter valset")
        else:
            repr_strings.append("Filters: %s | %s " % (self.export_filter, self.lexical_filter))
        repr_strings.append("Defining string: " + str(self.clause_set_string))
        repr_strings.append("ClauseBasedRule: "+str(self.clause_based_rule))
        return "\n".join(repr_strings)

    def process_metadata(self):
        if self.metadata_column is not None:
            f=self.metadata_column.split()
            # terminology of these next two variables comes from DMWB code
            self.export_filter=f[0][2:] # strip off first two characters (always W3?)
            self.lexical_filter=f[1]
            self.filter_flags={}
            for ifilter, filter_name in enumerate(["EXCLUDE_LINKAGE_ET_AL","EXCLUDE_INACTIVE_ET_AL","OBSOLETE_FILTER","EXCLUDE_CLINICALLY_UNLIKELY", "GLOBEX", "EXCLUDE_DRUGS_ET_AL"]):
                if filter_name!="OBSOLETE_FILTER":
                    self.filter_flags[filter_name]= str(ifilter) in self.export_filter
            self.apply_filters="F" in self.lexical_filter
        else:
            self.export_filter=""
            self.lexical_filter=""
            self.filter_flags={}
            self.apply_filters=False


class ValsetMembershipAnalysis():
    def __init__(self, valset=None, concepts=None, global_exclusions=None, stub_out_interaction_matrix_calc=False, verbose=False):
        self.clause_membership_analyses_list=[]
        # do membership analysis for each clause
        # full_exclusion_set=set(global_exclusions)
        full_exclusion_set=set()
        if not valset.is_a_filter_valset:
            # print("1 valset is not a filter valset")
            if valset.apply_filters:
                # print("2 Applying filters")
                for filter_name, filter_flag in valset.filter_flags.items():
                    # print("3a Filter", filter_name,"..")
                    if filter_flag:
                        # print("3b .. is applied")
                        # print("3c size is", len(valset.valset_collection.filter_memberships[filter_name]))
                        full_exclusion_set=full_exclusion_set.union(set(valset.valset_collection.filter_memberships[filter_name]))
        if verbose:
            print("Filters generate an exclusion set of size", len(full_exclusion_set))
        full_inclusion_set=set()
        final_inclusion_set=set()

        # loop over clauses and
        #   do ClauseMembershipAnalysis analysis on each
        #   assemble full inclusion and exclusion sets for valset
        #   get final_inclusion set using difference method on the above
        for clause in valset.clause_based_rule.clauses:
            # print("cma start..")
            clause_membership_analysis=ClauseMembershipAnalysis(clause=clause, concepts=concepts)
            # print("..cma done")
            
            self.clause_membership_analyses_list.append(clause_membership_analysis)
            if clause.clause_type=="exclude":
                full_exclusion_set=full_exclusion_set.union(set(clause_membership_analysis.members))
            else:   
                full_inclusion_set=full_inclusion_set.union(set(clause_membership_analysis.members))
        print("Got the clause memberships")
        # sys.exit()
        final_inclusion_set=full_inclusion_set.difference(full_exclusion_set)

        self.full_exclusion_list=list(full_exclusion_set)
        self.full_inclusion_list=list(full_inclusion_set)
        self.final_inclusion_list=list(final_inclusion_set)

        self.full_exclusion_list_n_members=len(self.full_exclusion_list)
        self.full_inclusion_list_n_members=len(self.full_inclusion_list)
        self.final_inclusion_list_n_members=len(self.final_inclusion_list)

        # loop over clauses amd make list of what they include once exclusions are applied
        # store this in the ValsetMembershipAnalysis (rather than the Clause equivalent) as
        # depends on the valset that the clause is in
        self.clause_members_after_exclusions_list=[]
        for i_clause, clause in enumerate(valset.clause_based_rule.clauses):
            if clause.clause_type=="include":
                trimmed_set=set(self.clause_membership_analyses_list[i_clause].members).difference(full_exclusion_set)
            else:
                # trimmed_set=[]
                trimmed_set=set(self.clause_membership_analyses_list[i_clause].members).intersection(full_inclusion_set)
            # the next variable needs renaming as in the case of exclusions it is the number of
            # members that were eligible for exclusion
            self.clause_members_after_exclusions_list.append(list(trimmed_set))
        
        # create interaction matrix:
        #       2D matrix (list of lists)
        #       diagonal elements are simply the memberships of each clause
        #       off diagonal elements are the overlaps between two clauses
        #       values are negative if either clause is an exclusion clause
        
        self.interaction_matrix=[]
        if stub_out_interaction_matrix_calc==True: # fill matrix with zeroes
            # matrix_size=len(self.clause_membership_analyses_list)
            # self.interaction_matrix=[ [0]*matrix_size ]*matrix_size
            self.interaction_matrix=[[]]
        else: # do potentially long calculation
            for clause_membership_analysis in self.clause_membership_analyses_list:
                interaction_row=[]
                s1=set(clause_membership_analysis.members)
                for clause2_membership_analysis in self.clause_membership_analyses_list:
                    s2=set(clause2_membership_analysis.members)
                    if s1==s2:
                        n=len(s1)
                    else:
                        n=len(s1.intersection(s2))
                    if "exclude" in [clause_membership_analysis.clause.clause_type,  clause2_membership_analysis.clause.clause_type]:
                        n=-n
                    interaction_row.append(n)
                self.interaction_matrix.append(interaction_row)
        
        #
        # Analyse the number of each semantic tag in the final inclusion list
        #
        self.semantic_tag_counts={}
        # for concept_id in self.final_inclusion_list:    # not sure why this sections seems to take so long?
        #     semantic_tag=concepts[concept_id].semantic_tag
        #     if semantic_tag not in self.semantic_tag_counts:
        #         self.semantic_tag_counts[semantic_tag]=0
        #     self.semantic_tag_counts[semantic_tag]+=1


        
        #
        # Consider adding here fancier stats like the total members that a clause contributes independedntly
        # of any other inclusion clause
        #