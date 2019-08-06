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
"""Base classes for rules."""

from os2datascanner.projects.admin.adminapp.models.sensitivity_level import Sensitivity


class Rule:
    def __init__(self, name, sensitivity=Sensitivity.HIGH):
        self.name = name
        self.sensitivity = sensitivity

    def _clamp_sensitivity(self, sensitivity_value):
        return min(sensitivity_value, self.sensitivity)

    """Represents a rule which can be executed on text and returns matches."""

    def execute(self, text):
        """Execute the rule on the given text.

        Return a list of MatchItem's.
        """
        raise NotImplementedError

    def is_all_match(self, matches):
        """
        Checks if each rule is matched with the provided list of matches
        :param matches: List of matches
        :return: {True | false}
        """
        # Most rules represent a single search, so the default implementation
        # of this method returns true if there were any matches
        return bool(matches)
