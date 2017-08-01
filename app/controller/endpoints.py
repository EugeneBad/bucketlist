from app.controller.views import Bucketlists, BucketlistDetail, BucketlistItems, \
    BucketListItemDetail, Register, Login


def api_endpoints(api):
    api.add_resource(Register, '/auth/register')

    api.add_resource(Login, '/auth/login')

    api.add_resource(Bucketlists, '/bucketlists')

    api.add_resource(BucketlistDetail, '/bucketlists/<int:bucketlist_id>')

    api.add_resource(BucketlistItems, '/bucketlists/<int:bucketlist_id>/items')

    api.add_resource(BucketListItemDetail, '/bucketlists/<int:bucketlist_id>/items/<int:item_id>')
