class MagicMockMixin:

    def get_mock_arg(self, mock_handler, arg):
        mock_args, _ = mock_handler.call_args
        return mock_args[1].get(arg)

    def get_mock_kwarg(self, mock_handler, kwarg):
        _, mock_kwargs = mock_handler.call_args
        return mock_kwargs.get(kwarg)
