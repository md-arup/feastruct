from feastruct.pre.material import Steel
from feastruct.pre.section import Section
import feastruct.fea.cases as cases
from feastruct.fea.frame_analysis import FrameAnalysis2D
from feastruct.solvers.linstatic import LinearStatic
from feastruct.solvers.linbuckling import LinearBuckling
from feastruct.solvers.feasolve import SolverSettings


# ------------
# preprocessor
# ------------

# constants & lists
L = 5000  # length of the beams
n_el = 12  # number of subdivisions for each beam
nodes = []  # list holding the node objects
elements = []  # list holding the element objects

# create 2d frame analysis object
analysis = FrameAnalysis2D()
analysis.post.n_subdiv = 5

# create materials and sections
steel = Steel()
section = Section(area=1000, ixx=8.333e5)

# create nodes
for i in range(n_el + 1):
    nodes.append(analysis.create_node(coords=[0, i * L / n_el]))

for i in range(n_el):
    elements.append(analysis.create_element(
        el_type='EB2-2D',
        nodes=[nodes[i], nodes[i+1]],
        material=steel,
        section=section
    ))

freedom_case = cases.FreedomCase()
freedom_case.add_nodal_support(node=nodes[0], val=0, dof=0)
freedom_case.add_nodal_support(node=nodes[0], val=0, dof=1)
freedom_case.add_nodal_support(node=nodes[-1], val=0, dof=0)

load_case = cases.LoadCase()
load_case.add_nodal_load(node=nodes[-2], val=-1e3, dof=1)

analysis_case = cases.AnalysisCase(freedom_case=freedom_case, load_case=load_case)

settings = SolverSettings()
settings.linear_static.time_info = True

LinearStatic(analysis=analysis, analysis_cases=[analysis_case], solver_settings=settings).solve()

# analysis.post.plot_geom(analysis_case=analysis_case, deformed=True, def_scale=25)

settings.linear_buckling.time_info = True
settings.linear_buckling.num_modes = 2
LinearBuckling(analysis=analysis, analysis_cases=[analysis_case], solver_settings=settings).solve()

for i in range(settings.linear_buckling.num_modes):
    analysis.post.plot_buckling_results(analysis_case=analysis_case, buckling_mode=i)
