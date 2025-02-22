%% orbital-agent/src/edge/coordinator.erl
-module(coordinator).
-behaviour(gen_server).

-export([start_link/0, dispatch_task/1]).
-export([init/1, handle_call/3, handle_cast/2]).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

dispatch_task(Task) ->
    gen_server:cast(?MODULE, {dispatch, Task}).

init([]) ->
    {ok, #{nodes => []}}.

handle_call(get_state, _From, State) ->
    {reply, State, State}.

handle_cast({dispatch, Task}, #{nodes := Nodes} = State) ->
    SelectedNode = select_node(Nodes),
    SelectedNode ! {execute, Task},
    {noreply, State}.

select_node(Nodes) ->
    % Edge node selection logic
    lists:nth(rand:uniform(length(Nodes)), Nodes).
