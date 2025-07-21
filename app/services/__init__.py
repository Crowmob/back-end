from app.services.user import UserServices

user_services = UserServices()

create_user = user_services.create_user
get_all_users = user_services.get_all_users
get_user_by_id = user_services.get_user_by_id
update_user = user_services.update_user
delete_user = user_services.delete_user
