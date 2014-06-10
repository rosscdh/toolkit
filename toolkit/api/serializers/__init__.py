# -*- coding: UTF-8 -*-
from .account import (AccountSerializer, PasswordSerializer)
from .activity import (MatterActivitySerializer, ItemActivitySerializer,)
from .client import (ClientSerializer, LiteClientSerializer)
from .discussion import (DiscussionCommentSerializer, DiscussionSerializer, LiteDiscussionSerializer)
from .matter import (MatterSerializer, LiteMatterSerializer, SimpleMatterSerializer)
from .item import (ItemSerializer, LiteItemSerializer,)
from .revision import (RevisionSerializer,)
from .review import (ReviewSerializer,)

from .sign import (SignatureSerializer,)

from .user import (UserSerializer,
                   LiteUserSerializer,
                   SimpleUserSerializer,
                   SimpleUserWithReviewUrlSerializer,
                   SimpleUserWithSignUrlSerializer)
# from .workflow import WorkflowSerializer
