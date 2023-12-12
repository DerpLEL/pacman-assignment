import requests
import json
from typing import List, Optional
from langchain.pydantic_v1 import BaseModel, Field
from langchain.chains.prompt_selector import ConditionalPromptSelector
from langchain.llms import LlamaCpp
from langchain.prompts import BasePromptTemplate, PromptTemplate
from langchain.llms.base import BaseLLM
from langchain.chains import LLMChain

class NER(BaseModel):
    """Abstract interface for Named Entity Recognition"""
    
    db: List[dict] = Field(
        ..., description="List of search queries to look up on Google"
    )
    llm_chain: LLMChain
    
    def __init__(self):
        
        self.db = [{
            "entity types": "PER",
            "description": "Person Name",
            "entity": ["Teacher name", "Student name"],
            "example": """Text:  < i> Yêu cầu khác < /i> . . . .  < b> Họ tên sinh viên < /b> . . Nguyễn Văn Tám. . . .  < b> Mã sinh viên < /b> . . XYZ123. . . .  < b> Nội dung yêu cầu < /b> . . Yêu cầu về việc chứng nhận hoàn thành môn học. . . .
Entities: Nguyễn Văn Tám is student name.
Text:  < b> MSSV/MSGV: 1512213 < /b>  . . . .  < i> Điểm thi >  Điểm môn học < /i> . . Vừa qua thầy Nguyễn Thanh Tuấn đã đăng điểm tổng kết môn Xử lí số tín hiệu lên trang điểm của trường , và em có một vài thắc mắc muốn hỏi thầy về điểm thành phần và điểm thi nhưng em không thể tìm thấy thông tin liên lạc của thầy .Mong thầy cô có thể cho em xin thông tin liên lạc của thầy Nguyễn Thanh Tuấn dạy bộ môn Xử lí số tín hiệu học kì vừa qua có được không ạ . Em xin cảm ơn thầy cô ạ . .
Entities: Nguyễn Thanh Tuấn is teacher name."""
    },
            {
            "entity types": "JOU",
            "description": "Journal",
            "entity": ["Journal", "Conference", "Workshop"],
            "example": """Text: <i>Yêu cầu khác</i>... <b>Tên hội nghị</b>. Hội nghị quốc tế về khoa học máy tính. ... <b>Tên tạp chí</b>. Journal of Artificial Intelligence Research. ...
Entities: Hội nghị quốc tế về khoa học máy tính is a conference. Journal of Artificial Intelligence Research is a journal.
Text: <i>Yêu cầu khác</i>... <b>Tên hội nghị</b>. ... <b>Tên tạp chí</b>... <b>Tên hội thảo</b>. Hội thảo "Hành trang cho tân sinh viên K24" đã diễn ra. ...
Entities: Hành trang cho tân sinh viên K24 is a workshop."""
    },
                {
                "entity types": "BOK",
                "description": "Book",
                "entity": ["Book","Document"],
                "example": """Text: <i> Loại tài liệu < /i> . . . .  <b> Tên sách < /b> . . "Lịch sử thế giới" . . .  <b> Mã tài liệu < /b> . . TLTG123. . . .  <b> Nội dung tài liệu < /b> . . Tài liệu này trình bày chi tiết lịch sử thế giới từ thời kỳ cổ đại đến hiện đại. . . .
Entities: "Lịch sử thế giới" is a book name.
Text:  <b> Mã tài liệu: DL201 < /b>  . . . .  <i> Tác giả >  Tài liệu < /i> . . Sách "Khoa học và Công nghệ hiện đại" đã được xuất bản vào năm 2020 và là một tài liệu tham khảo quan trọng về các phát triển trong lĩnh vực khoa học và công nghệ. Bạn có thể tìm thấy thông tin chi tiết trong tài liệu này về các khía cạnh của khoa học và công nghệ hiện đại. . . .
Entities: "Khoa học và Công nghệ hiện đại" is a document name."""        
    },
                {
                "entity types": "CRN",
                "description": "Course/Discipline Name",
                "entity": ["Course name","Discipline domain"], 
                "example": """< b> MSSV/MSGV: 41201960 < /b>  . . . .  < i> Học phí >  Học phí học kỳ chính < /i> . . . . Em chào thầy, cô quản trị viên. . . . Em tên là: Nguyễn Đình Long. . MSSV: 41201960. . Học khoa Điện-Điện tử, bộ môn Điện tử. . . . Cho em hỏi, Em đăng kí in thẻ sinh viên, sau đó vào BKpay để thanh toán phí. Khi đăng nhập bkpay xong, chọn khoản thanh toán rồi nhấn thanh toán, thì nó nhảy qua OCB. Nhưng sau khi đăng nhập OCB thì không thấy khoản thanh toán đâu cả (Em có đính kèm file chụp màn hình khi sau khi đăng nhập OCB phía dưới). Đáng lẽ nó hiện khoản thanh toán rồi mình nhấn vào xác nhận luôn. Nhưng me đã đăng xuất hết, rồi làm lại nhiều lần vẫn không được.. . Mong thầy cô khắc phục cho em ạ.. . . . Em cảm ơn.
Entities: Điện tử is discipline domain.
Text: <b>CRN/Subject Code: 1512213</b> . . . . <i> Điểm thi > Điểm môn học < /i> . . Vừa qua giáo viên Nguyễn Thanh Tuấn đã đăng điểm tổng kết môn Nguyên lí ngôn ngữ lập trình lên trang điểm của trường , và em có một vài thắc mắc muốn hỏi giáo viên về điểm thành phần và điểm thi nhưng em không thể tìm thấy thông tin liên lạc của giáo viên .Mong giáo viên có thể cho em xin thông tin liên lạc của giáo viên Nguyễn Thanh Tuấn dạy bộ môn Nguyên lí ngôn ngữ lập trình học kì vừa qua có được không ạ . Em xin cảm ơn giáo viên ạ . .
Entities: Nguyên lí ngôn ngữ lập trình is course name."""        
    },]

    @classmethod
    def from_llm(
        cls,
        llm: BaseLLM,
        prompt: Optional[BasePromptTemplate] = None
    ) -> "NER":
        
        """Initialize from llm using default template.

        Args:
            db: Hard-code database for storing few-shots and entities
            llm: llm for search question generation
            prompt: prompt to generating search questions
            
        Returns:
            NER
        """
        DEFAULT_LLAMA_PROMPT = """<s>[INST] <<SYS>>
Extract the following Target types from the Text. Don't explain anything. If you can't answer just output empty Python dictionary.
<</SYS>>

Target types: {entity}

{example}

Text: {input}
AI: [/INST]"""

        DEFAULT_PROMPT = """Extract the following Target types from the Text. Don't explain anything. If you can't answer just output empty Python dictionary.

Target types: {entity}

{example}

Text: {input}
AI: """

        prompt12 ="""<s>[INST] <<SYS>>
Extract the following Target types from the Text. Don't explain anything. If you can't answer just output empty Python dictionary.
<</SYS>>

Target types: request_category; student_name; student_id; request_content.

Text: '&lt i&gt Tốt nghiệp &lt /i&gt . . . .  &lt b&gt Họ tên sinh viên &lt /b&gt . . Nguyễn Quang Trường. . . .  &lt b&gt Mã sinh viên &lt /b&gt . . ABC123. . . .  &lt b&gt Nội dung yêu cầu &lt /b&gt . . Thưa thầy cô,. . em muốn biết em có đủ điều kiện tốt nghiệp không?. . . .'
AI: ```json
{"request_category": "Tốt nghiệp",
"student_name": "Nguyễn Quang Trường",
"student_id": "ABC123",
"request_content": "Thưa thầy cô, em muốn biết em có đủ điều kiện tốt nghiệp không?"}```
Text: '< i> Điểm thi < /i> . . . .  < b> Họ tên sinh viên < /b> . . Nguyễn Văn A. . . .  < b> Mã sinh viên < /b> . . BK1126. . . .  < b> Nội dung yêu cầu < /b> . . Chào thầy cô,. . . . Em muốn xin chấm phúc khảo lại bài thi "Tư tưởng Hồ Chí Minh" ạ!. . . . Em cảm ơn.. . . . '
AI: ```json
{"request_category": "Điểm thi",
"student_name": "Nguyễn Văn A",
"student_id": "BK1126",
"request_content": "Chào thầy cô, Em muốn xin chấm phúc khảo lại bài thi "Tư tưởng Hồ Chí Minh" ạ! Em cảm ơn."}```
Text: '&lt i&gt Yêu cầu khác &lt /i&gt . . . .  &lt b&gt Họ tên sinh viên &lt /b&gt . . Nguyễn Văn Tám. . . .  &lt b&gt Mã sinh viên &lt /b&gt . . XYZ123. . . .  &lt b&gt Nội dung yêu cầu &lt /b&gt . . Yêu cầu về việc chứng nhận hoàn thành môn học. . . . '
AI:  [/INST]"""

        if not prompt:
            QUESTION_PROMPT_SELECTOR = ConditionalPromptSelector(
                default_prompt=DEFAULT_PROMPT,
                conditionals=[
                    (lambda llm: isinstance(llm, LlamaCpp), DEFAULT_LLAMA_PROMPT)
                ],
            )
            prompt = QUESTION_PROMPT_SELECTOR.get_prompt(llm)
        
        # Use chat model prompt
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt
        )

        print(llm_chain)
        
        return None
    
        return cls(
            vectorstore=vectorstore,
            llm_chain=llm_chain,
            db=cls.db,
        )

    def qa_ner_prompt(str_prompt):
        # 1. Setting parameters for the POST request
        headers = {"Content-Type": "application/json; charset=utf-8"}
        url = 'https://bahnar.dscilab.com:20007/llama/api'

        data = {"prompt": str_prompt , "lang": "vi", "temperature": 0}
        json_data = json.dumps(data)

        # 2. Sending the POST request
        try:
            response = requests.post(url, headers=headers, data=json_data, timeout=100)
            response.raise_for_status()
            json_data = response.json()

        # Handle ConnectionError
        except requests.exceptions.ConnectionError as ce:
            print('Connection error:', ce)
        # Handle Timeout
        except requests.exceptions.Timeout as te:
            print('Request timed out:', te)
        # Handle HTTPError
        except requests.exceptions.HTTPError as he:
            print('HTTP error occurred:', he)
        # Handle ValueError
        except ValueError as ve:
            print('JSON decoding error:', ve)
        else:
            print('Request was successful')
            return json_data

# def test_01(prompt_index):
#     print('initing prompts')
#     prompts = init_prompt() # khởi tạo danh sách lời nhắc

#     prompt = prompts[prompt_index]

#     print('prompt: ', prompt)
#     print('--' * 30)

#     print('sending request')
#     result = qa_ner_prompt(prompt) # gọi api URA-LLMa

#     print(result) # in kết quả
#     print('--' * 30)

# test_01("12")

def readCommand( argv ):
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='mediumClassic')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default('the ghost agent TYPE in the ghostAgents module to use'),
                      metavar = 'TYPE', default='RandomGhost')
    parser.add_option('-k', '--numghosts', type='int', dest='numGhosts',
                      help=default('The maximum number of ghosts to use'), default=4)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-a','--agentArgs',dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed: random.seed('cs188')

    # Choose a layout
    args['layout'] = layout.getLayout( options.layout )
    if args['layout'] == None: raise Exception("The layout " + options.layout + " cannot be found")

    # Choose a Pacman agent
    noKeyboard = options.gameToReplay == None and (options.textGraphics or options.quietGraphics)
    pacmanType = loadAgent(options.pacman, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    if options.numTraining > 0:
        args['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts: agentOpts['numTraining'] = options.numTraining
    pacman = pacmanType(**agentOpts) # Instantiate Pacman with agentArgs
    args['pacman'] = pacman

    # Don't display training games
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # Choose a ghost agent
    ghostType = loadAgent(options.ghost, noKeyboard)
    args['ghosts'] = [ghostType( i+1 ) for i in range( options.numGhosts )]

    # Choose a display format
    if options.quietGraphics:
        import textDisplay
        args['display'] = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        textDisplay.SLEEP_TIME = options.frameTime
        args['display'] = textDisplay.PacmanGraphics()
    else:
        import graphicsDisplay
        args['display'] = graphicsDisplay.PacmanGraphics(options.zoom, frameTime = options.frameTime)
    args['numGames'] = options.numGames
    args['record'] = options.record
    args['catchExceptions'] = options.catchExceptions
    args['timeout'] = options.timeout

    # Special case: recorded games don't use the runGames method or args structure
    if options.gameToReplay != None:
        print(f'Replaying recorded game {options.gameToReplay}.')
        import cPickle
        f = open(options.gameToReplay)
        try: recorded = cPickle.load(f)
        finally: f.close()
        recorded['display'] = args['display']
        replayGame(**recorded)
        sys.exit(0)

    return args
    
if __name__ == '__main__':
    """
    The main function called when ner.py is run
    from the command line:

    > python ner.py

    See the usage string for more details.

    > python ner.py --help
    """
    # args = readCommand( sys.argv[1:] ) # Get game components based on input
    # runGames( **args )

    ner_api = NER()
    
    ner_api.from_llm()
    # import cProfile
    # cProfile.run("runGames( **args )")
    pass