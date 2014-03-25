# -*- coding: UTF-8 -*-
from .hateoas import HATOAS

from .account import (AccountSerializer, PasswordSerializer)
from .activity import (MatterActivitySerializer, ItemActivitySerializer,)
from .client import (ClientSerializer, LiteClientSerializer)
from .matter import (MatterSerializer, LiteMatterSerializer, SimpleMatterSerializer)
from .item import (ItemSerializer, LiteItemSerializer,)
from .revision import (RevisionSerializer,)
from .review import (ReviewSerializer,)
from .user import (UserSerializer,
                   LiteUserSerializer,
                   SimpleUserSerializer,
                   SimpleUserWithReviewUrlSerializer)
# from .workflow import WorkflowSerializer
