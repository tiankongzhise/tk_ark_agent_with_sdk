from src.tk_ark_agent_with_sdk.objects.free_walk_easy2.core import  Run
import  asyncio 


if __name__ == '__main__':
    run = Run(ai_model = 'DEEPSEEK-V3')
    asyncio.run(run.run())
