from rest_framework.response import Response


def validate_error(serialized):
    return Response(
        {
            'status': False,
            'message': serialized.errors,
            'data': ''
        },
        status=200
    )


def existence_error(object_name):
    return Response(
        {
            'status': False,
            'message': 'Object {} does not exist!'.format(object_name),
            'data': ''
        },
        status=200
    )


def successful_response(data, message='successful'):
    return Response(
        {
            'status': True,
            'message': message,
            'data': data
        },
        status=200
    )


def unsuccessful_response(message='unsuccessful', status=400):
    return Response(
        {
            'status': False,
            'message': message,
            'data': ''
        },
        status=status
    )


