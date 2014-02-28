# -*- coding: UTF-8 -*-
from .user import UserEndpoint
from .account import AccountEndpoint
from .client import ClientEndpoint
from .matter import (MatterEndpoint,
                     CategoryView as MatterCategoryView,
                     ClosingGroupView as MatterClosingGroupView,
                     MatterSortView,)

from .matter import (MatterItemsView,
                     MatterItemView,

                     ItemCurrentRevisionView as MatterItemCurrentRevisionView,
                     ItemSpecificReversionView as MatterItemSpecificReversionView,

                     ItemRevisionReviewerView,
                     ItemRevisionSignatoryView,
                     RemindReviewers,
                     RemindSignatories,)

from .item import ItemEndpoint
from .revision import RevisionEndpoint
# from .workflow import WorkflowEndpoint