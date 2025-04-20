from copy import deepcopy


def format_dict(bot_parametrs: dict, post) -> dict:
    current_params = deepcopy(bot_parametrs)

    post_text = current_params['query'].format(query=post.text)
    post_path = current_params['path'].format(name=post.id)

    current_params['query'] = post_text.replace('*', '')
    current_params['path'] = post_path

    return current_params