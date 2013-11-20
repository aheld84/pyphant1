# -*- coding: utf-8 -*-

# Copyright (c) 2006-2013, Rectorate of the University of Freiburg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def ensure_mpl_backend(backend=None):
    """
    Tries to select the matplotlib backend.

    Raises EnvironmentError, if the desired backend is valid but could not be selected.
    If `backend` is None, either 'agg' or 'wxagg' is chosen, depending on whether
    a display is present (on Linux and Darwin).
    For other platforms, 'wxagg' is always the default.
    Returns the selected backend as given by matplotlib.get_backend().
    """
    if backend is None:
        import platform
        import os
        if platform.system() in ('Linux', 'Darwin') and not 'DISPLAY' in os.environ:
            backend = 'agg'
        else:
            backend = 'wxagg'
    import matplotlib
    active_backend = matplotlib.get_backend()
    if active_backend.lower() != backend.lower():
        matplotlib.use(backend)
        active_backend = matplotlib.get_backend()
        if active_backend.lower() != backend.lower():
            raise EnvironmentError(
                "Could not select matplotlib backend '%s' ('%s' is active)!" \
                % (backend, active_backend)
                )
    return active_backend
