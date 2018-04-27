import unittest
import logging

import grpc
import services.face_detect_server
import services.grpc.face_detect_pb2_grpc

from services.face_detect_client import find_faces
from faceutils import render_face_detect_debug_image
from tests.test_images import one_face, multiple_faces, no_faces

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web

log = logging.getLogger("test.face_detect")


class TestFaceDetectJSONRPC(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        app = web.Application()
        app.router.add_post('/', services.face_detect_server.handle)
        return app

    @unittest_run_loop
    async def test_example(self):
        import base64
        with open(one_face[0], "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('ascii')

        rpc_dict = {
            "jsonrpc": "2.0",
            "method": "find_face",
            "id": "1",
            "params": {
                "algorithm": "dlib_hog",
                "image": img_base64
            }
        }

        resp = await self.client.post('/', json=rpc_dict)
        assert resp.status == 200
        json = await resp.json()
        print(json)
        assert "faces" in json['result']


class BaseTestCase:
    class BaseTestFaceDetectGRPC(unittest.TestCase):
        test_port = 50001
        server = None

        @classmethod
        def setUpClass(cls):
            cls.server = services.face_detect_server.serve(algorithm=cls.algorithm, max_workers=2, port=cls.test_port)

        @classmethod
        def tearDownClass(cls):
            cls.server.stop(0)

        def setUp(self):
            self.channel = grpc.insecure_channel('localhost:' + str(self.test_port))
            self.stub = services.grpc.face_detect_pb2_grpc.FaceDetectStub(self.channel)

        def tearDown(self):
            pass

class TestFaceDetectGRPC_DlibCNN(BaseTestCase.BaseTestFaceDetectGRPC):
    algorithm = 'dlib_cnn'

    def test_find_single_face(self):
        for img_fn in one_face:
            log.debug("Testing face detect %s on file with a single face %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            log.debug(str(result.face_bbox))
            self.assertEqual(len(result.face_bbox), 1)
            render_face_detect_debug_image(self, img_fn, result)

    def test_find_multiple_faces(self):
        for img_fn in multiple_faces:
            log.debug("Testing face detect %s on file with multiple faces %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            self.assertGreater(len(result.face_bbox), 1)
            log.debug(str(result.face_bbox))
            render_face_detect_debug_image(self, img_fn, result)

    def test_find_no_faces(self):
        for img_fn in no_faces:
            log.debug("Testing face detect %s on file with no faces %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            self.assertEqual(len(result.face_bbox), 0)
            log.debug(str(result.face_bbox))
            render_face_detect_debug_image(self, img_fn, result)

class TestFaceDetectGRPC_DlibHOG(BaseTestCase.BaseTestFaceDetectGRPC):
    algorithm = 'dlib_hog'

    def test_find_single_face(self):
        for img_fn in one_face:
            log.debug("Testing face detect %s on file with a single face %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            log.debug("%s - %s - %s" % (self.algorithm, img_fn, str(result.face_bbox)))
            self.assertEqual(len(result.face_bbox), 1)
            render_face_detect_debug_image(self, img_fn, result)

    def test_find_multiple_faces(self):
        for img_fn in multiple_faces:
            log.debug("Testing face detect %s on file with multiple faces %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            self.assertGreater(len(result.face_bbox), 1)
            log.debug("%s - %s - %s" % (self.algorithm, img_fn, str(result.face_bbox)))
            render_face_detect_debug_image(self, img_fn, result)

    def test_find_no_faces(self):
        for img_fn in no_faces:
            log.debug("Testing face detect %s on file with no faces %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            self.assertEqual(len(result.face_bbox), 0)
            log.debug("%s - %s - %s" % (self.algorithm, img_fn, str(result.face_bbox)))
            render_face_detect_debug_image(self, img_fn, result)

class TestFaceDetectGRPC_HaarCascade(BaseTestCase.BaseTestFaceDetectGRPC):
    algorithm = 'haar_cascade'

    def test_find_single_face(self):
        for img_fn in one_face:
            log.debug("Testing face detect %s on file with a single face %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            log.debug(str(result.face_bbox))
            self.assertEqual(len(result.face_bbox), 1)
            render_face_detect_debug_image(self, img_fn, result)

    def test_find_multiple_faces(self):
        for img_fn in multiple_faces:
            log.debug("Testing face detect %s on file with multiple faces %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            if img_fn.endswith('classroom_in_tanzania.jpg'):
                log.debug("Haar cascade is known to fail on %s" % (img_fn,))
            else:
                self.assertGreater(len(result.face_bbox), 1)
            log.debug(str(result.face_bbox))
            render_face_detect_debug_image(self, img_fn, result)

    def test_find_no_faces(self):
        for img_fn in no_faces:
            log.debug("Testing face detect %s on file with no faces %s" % (self.algorithm, img_fn,))
            result = find_faces(self.stub, img_fn)
            self.assertEqual(len(result.face_bbox), 0)
            log.debug(str(result.face_bbox))
            render_face_detect_debug_image(self, img_fn, result)


if __name__ == '__main__':
    unittest.main()