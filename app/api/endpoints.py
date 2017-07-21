from app.api.views import Bucketlists, BucketlistDetail, BucketlistItems, \
    BucketListItemDetail, Register, Login


def api_endpoints(api):
    api.add_resource(Register, '/api/V1/auth/register')

    api.add_resource(Login, '/api/V1/auth/login')

    api.add_resource(Bucketlists, '/api/V1/bucketlists')

    api.add_resource(BucketlistDetail, '/api/V1/bucketlists/<int:bucketlist_id>')

    api.add_resource(BucketlistItems, '/api/V1/bucketlists/<int:bucketlist_id>/items')

    api.add_resource(BucketListItemDetail, '/api/V1/bucketlists/<int:bucketlist_id>/items/<int:item_id>')
