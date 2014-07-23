# -*- coding: UTF-8 -*-
from .user import UserEndpoint

from .account import AccountEndpoint

from .activity import (ActivityEndpoint,
                       MatterActivityEndpoint,
                       ItemActivityEndpoint)

from .client import ClientEndpoint

from .matter import (MatterEndpoint,
                     ClosingGroupView as MatterClosingGroupView,
                     RevisionLabelView as MatterRevisionLabelView,
                     MatterExportView)

from .review import (ReviewEndpoint,
                     ItemRevisionReviewersView,
                     ItemRevisionReviewerView,
                     ReviewerHasViewedRevision,)

from .sign import   (SignatureEndpoint,
                     ItemRevisionSignersView,
                     ItemRevisionSignerView,)

from .sort import (MatterSortView,)

from .category import (CategoryView as MatterCategoryView,)

from .participant import (MatterParticipant,)

from .revision import (ItemCurrentRevisionView as MatterItemCurrentRevisionView,
                       ItemSpecificReversionView as MatterItemSpecificReversionView,)

from .attachment import (AttachmentView, AttachmentEndpoint)

from .revision_request import (ItemRequestRevisionView as MatterItemRequestRevisionView,)

from .item import (ItemEndpoint,
                   MatterItemsView,
                   MatterItemView,)

from .reminder import (RemindReviewers,
                       RemindSignatories,
                       RemindRequestedRevisionInvitee,
                       ItemTaskReminderView)

from .revision import RevisionEndpoint
# from .workflow import WorkflowEndpoint

from .comment import ItemCommentEndpoint
from .discussion import ItemDiscussionCommentEndpoint
from .discussion import MatterDiscussionEndpoint, MatterDiscussionCommentEndpoint, MatterDiscussionParticipantEndpoint

from .task import TaskEndpoint, ItemTasksView, ItemTaskView
