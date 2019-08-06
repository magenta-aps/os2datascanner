# -*- coding: UTF-8 -*-
# encoding: utf-8
# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )

from django.db import models

from .rule_model import Rule


class NameRule(Rule):
    DATABASE_DST_2014 = 0

    database_choices = (
        (DATABASE_DST_2014,
         u'Danmarks Statistiks liste over navne pr. 1. januar 2014'), )

    database = models.IntegerField(
        choices=database_choices,
        default=DATABASE_DST_2014,
        verbose_name="Navnedatabase")

    whitelist = models.TextField(
        blank=True, default="", verbose_name='Godkendte navne')
    blacklist = models.TextField(
        blank=True, default="", verbose_name='Sortlistede navne')
