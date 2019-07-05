from .core import Source, Handle, ShareableCookie
from .file import FilesystemResource

from os import rmdir
from regex import compile
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from pathlib import Path
from tempfile import mkdtemp
from subprocess import run

class SMBSource(Source):
    def __init__(self, unc, user=None, password=None, domain=None):
        self._unc = unc
        self._user = user
        self._password = password
        self._domain = domain

    def _make_optarg(self, display=True):
        optarg = ["ro"]
        if self._user:
            optarg.append('user=' + self._user)
        if self._password:
            optarg.append(
                    'password=' + (self._password if not display else "****"))
        else:
            optarg.append('guest')
        if self._domain:
            optarg.append('domain=' + self._domain)
        return ",".join(optarg)

    def __str__(self):
        return "SMBSource({0}, {1})".format(self._unc, self._make_optarg())

    def _open(self, sm):
        mntdir = mkdtemp()
        try:
            args = ["mount", "-t", "cifs", self._unc, mntdir, '-o']
            args.append(self._make_optarg(display=False))
            print(args)
            assert run(args).returncode == 0
            return ShareableCookie(Path(mntdir))
        except:
            rmdir(mntdir)
            raise

    def _close(self, mntdir):
        mntdir = str(mntdir)
        args = ["umount", mntdir]
        try:
            assert run(args).returncode == 0
        except:
            raise
        finally:
            rmdir(mntdir)

    def handles(self, sm):
        mntdir = sm.open(self)
        for d in mntdir.glob("**"):
            for f in d.iterdir():
                if f.is_file():
                    yield SMBHandle(self, f.relative_to(mntdir))

    # Third form from https://www.iana.org/assignments/uri-schemes/prov/smb
    def to_url(self):
        server, path = self._unc.lstrip('/').split('/', maxsplit=1)
        netloc = ""
        if self._user:
            if self._domain:
                netloc += self._domain + ";"
            netloc += self._user
            if self._password:
                netloc += ":" + self._password
            netloc += "@"
        netloc += server
        return urlunsplit(('smb', netloc, quote(path), None, None))

    netloc_regex = compile(r"^(((\w+);)?(\w+)(:(\w+))?@)?([\w.]+)$")
    @staticmethod
    @Source.url_handler("smb")
    def from_url(url):
        scheme, netloc, path, _, _ = urlsplit(url)
        match = SMBSource.netloc_regex.match(netloc)
        if match:
            _, _, domain, username, _, password, unc = match.groups()
            return SMBSource("//" + unc + unquote(path),
                username or None, password or None, domain or None)
        else:
            return None

class SMBHandle(Handle):
    def follow(self, sm):
        return FilesystemResource(self, sm)