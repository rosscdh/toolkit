# -*- coding: UTF-8 -*-
from .user import UserEndpoint

from .account import AccountEndpoint

from .activity import (ActivityEndpoint,
                       MatterActivityEndpoint,
                       ItemActivityEndpoint)

from .client import ClientEndpoint

from .matter import (MatterEndpoint,
                     ClosingGroupView as MatterClosingGroupView,)

from .review import (ItemRevisionReviewersView,
                     ItemRevisionReviewerView,)

from .sign import   (ItemRevisionSignatoriesView,
                     ItemRevisionSignatoryView,)

from .sort import (MatterSortView,)

from .category import (CategoryView as MatterCategoryView,)

from .participant import (MatterParticipant,)

from .revision import (ItemCurrentRevisionView as MatterItemCurrentRevisionView,
                       ItemSpecificReversionView as MatterItemSpecificReversionView,)

from .item_request import (ItemRequestRevisionView as MatterItemRequestRevisionView,)

from .item import (ItemEndpoint,
                   MatterItemsView,
                   MatterItemView,)

from .reminder import (RemindReviewers,
                       RemindSignatories)

from .revision import RevisionEndpoint
# from .workflow import WorkflowEndpoint