from os import listdir
import pdfrw
from tempfile import TemporaryDirectory
from subprocess import run

from ..core import Handle, Source, Resource, SourceManager
from ..file import FilesystemResource
from .derived import DerivedSource


PAGE_TYPE = "application/x.os2datascanner.pdf-page"


@Source.mime_handler("application/pdf")
class PDFSource(DerivedSource):
    type_label = "pdf"

    def _generate_state(self, sm):
        with self.handle.follow(sm).make_path() as p:
            # Explicitly download the file here for the sake of PDFPageSource,
            # which needs a local filesystem path to pass to pdftohtml
            yield p

    def handles(self, sm):
        reader = pdfrw.PdfReader(sm.open(self))
        for i in range(1, len(reader.pages) + 1):
            yield PDFPageHandle(self, str(i))


class PDFPageResource(Resource):
    def compute_type(self):
        return PAGE_TYPE


@Handle.stock_json_handler("pdf-page")
class PDFPageHandle(Handle):
    type_label = "pdf-page"
    resource_type = PDFPageResource

    @property
    def presentation(self):
        return "page {0} of {1}".format(self.relative_path, self.source.handle)

    def censor(self):
        return PDFPageHandle(self.source.censor(), self.relative_path)

    def guess_type(self):
        return PAGE_TYPE


@Source.mime_handler(PAGE_TYPE)
class PDFPageSource(DerivedSource):
    type_label = "pdf-page"

    def _generate_state(self, sm):
        # As we produce FilesystemResources, we need to produce a cookie of the
        # same format as FilesystemSource: a filesystem directory in which to
        # interpret relative paths
        page = self.handle.relative_path
        path = sm.open(self.handle.source)
        with TemporaryDirectory() as tmpdir:
            run(["pdftohtml",
                    "-q", "-nodrm", "-noframes",
                    "-f", page, "-l", page,
                    # Explicitly scaling up output images makes tesseract(1) do
                    # a better job. (Presumably this is because less detail is
                    # lost?)
                    "-s", "-c", "-zoom", "3.0",
                    path,
                    # Trick pdftohtml into writing to our temporary directory
                    # (groan...)
                    "{0}/out".format(tmpdir)])
            yield tmpdir

    def handles(self, sm):
        for p in listdir(sm.open(self)):
            yield PDFObjectHandle(self, p)


@Handle.stock_json_handler("pdf-object")
class PDFObjectHandle(Handle):
    type_label = "pdf-object"
    resource_type = FilesystemResource

    @property
    def presentation(self):
        return "{0} (on {1})".format(self.relative_path, self.source.handle)

    def censor(self):
        return PDFObjectHandle(self.source.censor(), self.relative_path)
