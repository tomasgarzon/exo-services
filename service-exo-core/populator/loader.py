import yaml

from .exo_account.exo_account_loader import exo_account_constructor
from .consultant.consultant_loader import consultant_constructor
from .sprint_automated.sprint_automated_loader import sprint_automated_constructor
from .generic_project.generic_project_loader import generic_project_constructor
from .customer.customer_loader import customer_constructor
from .team.team_loader import team_constructor
from .qa_session.qa_session_loader import qa_session_constructor
from .circles.circles_loader import circle_constructor


# Custom constructors
yaml.Loader.add_constructor('!exo_account', exo_account_constructor)
yaml.Loader.add_constructor('!consultant', consultant_constructor)
yaml.Loader.add_constructor('!sprint_automated', sprint_automated_constructor)
yaml.Loader.add_constructor('!generic_project', generic_project_constructor)
yaml.Loader.add_constructor('!customer', customer_constructor)
yaml.Loader.add_constructor('!team', team_constructor)
yaml.Loader.add_constructor('!qa_session', qa_session_constructor)
yaml.Loader.add_constructor('!circle', circle_constructor)
