load("//sematic:wheel_constants.bzl",
    "wheel_version_string",
    "wheel_author",
    "wheel_author_email",
    "wheel_classifiers",
    "wheel_description_file",
    "wheel_entry_points",
    "wheel_homepage",
    "wheel_platform",
    "wheel_python_requires",
    "wheel_python_tag",
    "wheel_requires",
    "wheel_deps",
)
load(
    "//sematic/ee:extras.bzl",
    "EXTRA_REQUIRES",
    "EXTRA_SEMATIC_DEPS",
)

sematic_py_lib(
    name = "init",
    srcs = ["__init__.py"],
    deps = [
        ":calculator",
        ":container_images",
        ":resolver",
        ":retry_settings",
        "//sematic:future_context",
        "//sematic/future_operators:init",
        "//sematic/plugins/external_resource:timed_message",
        "//sematic/plugins/kuberay_wrapper:standard",
        "//sematic/resolvers:cloud_resolver",
        "//sematic/resolvers:local_resolver",
        "//sematic/resolvers:resource_requirements",
        "//sematic/resolvers:worker",
        "//sematic/types:casting",
        "//sematic/types:init",
        "//sematic/utils:exceptions",
    ],
)

sematic_py_lib(
    name = "abstract_plugin",
    srcs = ["abstract_plugin.py"],
    deps = [
        "//sematic/utils:exceptions",
    ],
)

sematic_py_lib(
    name = "container_images",
    srcs = ["container_images.py"],
    deps = [],
)

sematic_py_lib(
    name = "api_client",
    srcs = ["api_client.py"],
    pip_deps = [
        "requests",
    ],
    # buildifier: leave-alone
    deps = [
        "//sematic:abstract_future",
        "//sematic:versions",
        "//sematic/api/endpoints:auth",
        "//sematic/config:config",
        "//sematic/config:settings",
        "//sematic/config:user_settings",
        "//sematic/db/models:artifact",
        "//sematic/db/models:edge",
        "//sematic/db/models:external_resource",
        "//sematic/db/models:factories",
        "//sematic/db/models:resolution",
        "//sematic/db/models:run",
        "//sematic/db/models:user",
        "//sematic/plugins:abstract_external_resource",
        "//sematic/utils:retry",
    ],
)

sematic_py_lib(
    name = "future_context",
    srcs = ["future_context.py"],
    deps = [
        "//sematic:abstract_future",
        "//sematic/utils:exceptions",
    ],
)

sematic_py_lib(
    name = "log_reader",
    srcs = ["log_reader.py"],
    pip_deps = [
        "requests",
    ],
    deps = [
        "//sematic:abstract_future",
        "//sematic:api_client",
        "//sematic/db:queries",
        "//sematic/db/models:resolution",
        "//sematic/db/models:run",
        "//sematic/plugins/storage:s3_storage",
        "//sematic/resolvers:cloud_resolver",
        "//sematic/scheduling:external_job",
    ],
)

sematic_py_lib(
    name = "client",
    srcs = ["client.py"],
    deps = [
        ":api_client",
    ],
)

sematic_py_lib(
    name = "abstract_calculator",
    srcs = ["abstract_calculator.py"],
    deps = [],
)

sematic_py_lib(
    name = "abstract_future",
    srcs = ["abstract_future.py"],
    deps = [
        ":abstract_calculator",
        ":retry_settings",
        "//sematic/resolvers:resource_requirements",
    ],
)

sematic_py_lib(
    name = "calculator",
    srcs = ["calculator.py"],
    deps = [
        ":abstract_calculator",
        ":future",
        ":retry_settings",
        "//sematic:future_context",
        "//sematic/resolvers:resource_requirements",
        "//sematic/resolvers:type_utils",
        "//sematic/types:casting",
        "//sematic/types:init",
        "//sematic/types:registry",
        "//sematic/types:type",
        "//sematic/utils:algorithms",
        "//sematic/utils:memoized_property",
    ],
)

sematic_py_lib(
    name = "future",
    srcs = ["future.py"],
    deps = [
        ":abstract_calculator",
        ":abstract_future",
        "//sematic:resolver",
        "//sematic/resolvers:local_resolver",
        "//sematic/resolvers:resource_requirements",
        "//sematic/resolvers:silent_resolver",
    ],
)

sematic_py_lib(
    name = "resolver",
    srcs = ["resolver.py"],
    deps = [
        ":abstract_future",
    ],
)

sematic_py_lib(
    name = "retry_settings",
    srcs = ["retry_settings.py"],
    deps = [
        "//sematic/utils:exceptions",
    ],
)

sematic_py_lib(
    name = "storage",
    srcs = ["storage.py"],
    pip_deps = [
        "boto3",
    ],
    # buildifier: leave-alone
    deps = [
        "//sematic/config:config",
        "//sematic/config:server_settings",
        "//sematic/config:user_settings",
        "//sematic/utils:memoized_property",
        "//sematic/utils:retry",
    ],
)

sematic_py_lib(
    name = "versions",
    srcs = ["versions.py"],
    deps = [],
)

sematic_py_lib(
    name = "graph",
    srcs = ["graph.py"],
    deps = [
        ":abstract_future",
        ":api_client",
        "//sematic/db/models:artifact",
        "//sematic/db/models:edge",
        "//sematic/db/models:factories",
        "//sematic/db/models:run",
        "//sematic/resolvers:type_utils",
        "//sematic/utils:algorithms",
        "//sematic/utils:memoized_property",
    ],
)

sematic_py_wheel(
    name = "wheel",
    author = wheel_author,
    author_email = wheel_author_email,
    classifiers = wheel_classifiers,
    description_file = wheel_description_file,
    distribution = "sematic",
    entry_points = wheel_entry_points,
    homepage = wheel_homepage,
    license = "Apache License 2.0",
    platform = wheel_platform,
    python_requires = wheel_python_requires,
    python_tag = wheel_python_tag,
    requires = wheel_requires,
    version = wheel_version_string,
    extra_requires = EXTRA_REQUIRES,
    visibility = ["//visibility:public"],
    deps = wheel_deps + EXTRA_SEMATIC_DEPS,
)
