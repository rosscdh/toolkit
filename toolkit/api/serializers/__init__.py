# -*- coding: UTF-8 -*-
from .hateoas import HATOAS

from .account import (AccountSerializer, PasswordSerializer)
from .activity import (MatterActivitySerializer, ItemActivitySerializer,)
from .client import (ClientSerializer, LiteClientSerializer)
from .matter import (MatterSerializer, LiteMatterSerializer)
from .item import (ItemSerializer,)
from .revision import (RevisionSerializer,)
from .user import (UserSerializer, LiteUserSerializer, SimpleUserSerializer,)
# from .workflow import WorkflowSerializer
