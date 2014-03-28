# -*- coding: UTF-8 -*-
from .endpoints.client import (ClientsTest,)
from .endpoints.matter import (MattersTest,
                               MatterPercentageTest,
                               MatterDetailTest,
                               MatterDetailProvidedDataTest)
from .endpoints.review import *
from .endpoints.item_request import *
from .endpoints.item import (ItemsTest, ItemDetailTest, ItemDataTest)
from .endpoints.sort import (MatterSortTest,)
from .endpoints.participant import (MatterParticipantTest,)
from .endpoints.category import (MatterCategoryTest,)
from .endpoints.revision import *
from .endpoints.user import (UsersTest,)
from .endpoints.activity import (ItemActivityEndpointTest, MatterActivityEndpointTest)
from .endpoints.remind import *
from .endpoints.comment import (CommentTest, )
